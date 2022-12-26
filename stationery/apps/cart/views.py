from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.db import transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from accounts.utils import normalize_email
from cart.cart import Cart
from cart.conf import CART_KEY
from cart.forms import CartItemFormSet
from lib.email import create_email
from orders.forms import YaPaymentForm
from orders.models import DeliveryType, Item, Order, OrderStatus
from orders.utils import fetch_delivery_price
from yandex_kassa.models import PaymentMethod


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


class PaymentView(FormView):
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

    def get_initial(self):
        """
        Контактные данные из профиля пользователя.
        """
        user = self.request.user

        return {
            'email': user.email,
            'phone': user.phone,
            'delivery_type': DeliveryType.EXW,
            'delivery_address': '',
            'zip_code': '',
            'weight': Cart(self.request).get_total_weight(),
        }

    def get_form_kwargs(self):
        """
        Если пользователь зарегистрирован, то запрещаем редактировать почту и
        телефон.
        """
        form_kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            form_kwargs['disabled_fields'] = ['email']
            form_kwargs['is_wholesaler'] = self.request.user.is_wholesaler
        return form_kwargs

    def form_valid(self, form):
        """
        Если форма валидна, то нам нужно создать заказ и отправить клиента на
        оплату, если это физ. лицо. Если это юр. лицо, то сказать, что заказ
        обрабатывается.
        """
        cart = Cart(self.request)
        if cart.get_total_price() == 0:
            return self.form_invalid(form)

        if not self.request.user.is_authenticated:
            data = form.cleaned_data
            created, user = self.get_or_create_user(data['email'],
                                                    data['phone'])
            if created:
                login(self.request, user)
            else:
                login_url = reverse('account:login')
                payment_url = reverse('account:payment')
                return redirect(f'{login_url}?next={payment_url}')

        self.success_url = self.create_order(form)
        cart.clear()  # очищаем корзину.
        return super().form_valid(form)

    def get_or_create_user(self, email, phone):
        """
        Возвращает пользователя, если он есть, если нет, то вначале
        регистрирует его.
        """
        User = get_user_model()

        try:
            user = User.objects.get(email=normalize_email(email))
            return (False, user)
        except User.DoesNotExist:
            password = User.objects.make_random_password()
            user = User.objects.create_user(
                email=normalize_email(email),
                password=password,
                phone=phone,
            )

            body_html = render_to_string(
                'email/auto_registered_user.html',
                {
                    'site': settings.DEFAULT_DOMAIN,
                    'username': user.email,
                    'password': password,
                }
            )

            email = create_email(
                'Спасибо за регистрацию!',
                body_html,
                user.email
            )

            email.send()

            return (True, user)

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
