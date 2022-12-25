from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from yandex_kassa.models import PaymentMethod

from cart.cart import Cart
from cart.conf import CART_KEY
from cart.forms import CartItemFormSet

from orders.forms import YaPaymentForm
from orders.models import DeliveryType, Item, Order, OrderStatus
from orders.utils import fetch_delivery_price


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
            return HttpResponseRedirect(reverse('account:login') +
                                        '?next=%s' % reverse('account:cart'))

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
        self.request.session[CART_KEY] = cart_items
        self.request.session.modified = True
        return super().form_valid(form)


class PaymentView(LoginRequiredMixin, FormView):
    """
    Страница оплаты и доставки.
    """
    form_class = YaPaymentForm
    template_name = 'cart/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        user = cart.request.user
        context.update({
            'is_opt': user.is_wholesaler,
        })
        return context

    def get_form_kwargs(self):
        """
        Передаём данные для создания формы оплаты.
        """
        kwargs = {}

        if self.request.method == 'GET':
            cart = Cart(self.request)

            kwargs['initial'] = {
                'phone': self.request.user.phone,
                'email': self.request.user.email,
                'delivery_type': DeliveryType.EXW,
                'delivery_address': '',
                'zip_code': '',
                'weight': cart.get_total_weight(),
            }

        elif self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs

    def form_valid(self, form):
        """
        Если форма валидна, то нам нужно создать заказ и отправить клиента на
        оплату, если это физ. лицо. Если это юр. лицо, то сказать, что заказ
        обрабатывается.
        """
        cart = Cart(self.request)
        if cart.get_total_price() == 0:
            return self.form_invalid(form)
        self.success_url = self.create_order(form)
        cart.clear()  # очищаем корзину.
        return super().form_valid(form)

    def create_order(self, form):
        """
        Создаём заказ .
        """
        data = form.cleaned_data
        cart = Cart(self.request)
        user = cart.request.user

        with transaction.atomic():
            order_data = {
                'user': user,
                'status': OrderStatus.INWORK,
                'comment': data['comment'],
                'delivery_type': data['delivery_type'] or DeliveryType.EXW,
                'delivery_address': data['delivery_address'],
                'zip_code': data['zip_code'],
            }

            if not user.is_wholesaler:
                order_data['delivery_price'] = fetch_delivery_price(
                    data['delivery_type'],
                    '142200',
                    data['zip_code'],
                    cart.get_total_weight())

                if data['payment_method_data'] == PaymentMethod.CASH:
                    order_data['status'] = OrderStatus.CONFIRMED

            if user.is_wholesaler:
                order_data['status'] = OrderStatus.CONFIRMED

            order = Order.objects.create(**order_data)

            for item in cart:
                offer = item['instance']

                Item.objects.create(**{
                    'order': order,
                    'offer': offer,
                    'quantity': item['quantity'],
                    'unit_price': offer.retail_price,
                })

            if not user.is_wholesaler:
                if data['payment_method_data'] != PaymentMethod.CASH:
                    return form.create_payment(
                        request=self.request, order=order, payer=user)

            order.send_client_email()
            order.send_manager_email()
            return reverse('account:history_detail', kwargs={'pk': order.pk})
