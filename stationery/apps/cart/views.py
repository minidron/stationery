from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import FormView

from cart.cart import Cart
from cart.conf import CART_SESSION_ID
from cart.forms import CartItemFormSet

from orders.forms import YaPaymentForm
from orders.models import DeliveryType, Item, Order, OrderStatus


class CartView(FormView):
    """
    Страница корзины.
    """
    form_class = CartItemFormSet
    success_url = reverse_lazy('account:payment')
    template_name = 'cart/cart.html'

    def get_form_kwargs(self):
        """
        Передаём корзину пользователя в форму.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'cart': Cart(self.request),
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        Валидация всех форм.
        """
        cart_form = self.get_form()
        user = cart_form.cart.request.user

        # Пользователь не авторизован.
        if not user.is_authenticated:
            return self.form_invalid(cart_form)

        if cart_form.is_valid():
            return self.form_valid(cart_form)
        else:
            return self.form_invalid(cart_form)

    def form_valid(self, form):
        """
        Для уверенности мы пересохраняем данные из формы в сессию пользователя.
        """
        cart_items = {}
        for offer_form in form.forms:
            offer_form.is_valid()
            cart_items[str(offer_form.offer.pk)] = {
                'quantity': offer_form.cleaned_data['quantity'],
            }
        self.request.session[CART_SESSION_ID] = cart_items
        self.request.session.modified = True
        return super().form_valid(form)


class PaymentView(LoginRequiredMixin, FormView):
    """
    Страница оплаты и доставки.
    """
    form_class = YaPaymentForm
    template_name = 'cart/payment.html'

    def get_form_kwargs(self):
        """
        Передаём данные для создания формы оплаты.
        """
        kwargs = {
            'prefix': 'payment',
        }

        if self.request.method == 'GET':
            cart = Cart(self.request)

            kwargs['initial'] = {
                'phone': self.request.user.profile.phone,
                'email': self.request.user.email,
                'delivery_type': DeliveryType.EXW,
                'delivery_address': '',
                'zip_code': '',
                'weight': cart.get_total_weight(),
            }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs

    def create_order(self, cart_form):
        """
        Создаём заказ .
        """
        cart = cart_form.cart
        user = cart.request.user

        with transaction.atomic():
            order = Order.objects.create(**{
                'user': user,
                'status': OrderStatus.INWORK,
            })

            for item in cart:
                offer = item['instance']

                Item.objects.create(**{
                    'order': order,
                    'offer': offer,
                    'quantity': item['quantity'],
                    'unit_price': offer.retail_price,
                })
