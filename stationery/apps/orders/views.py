from django.conf import settings
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, FormView, ListView, TemplateView

from password_reset.views import Recover, RecoverDone, Reset

from cart.cart import Cart
from cart.conf import CART_KEY
from lib.email import create_email
from orders.forms import (
    CompanyRegistrationForm, ItemFormSet, OrderForm, RegistrationForm,
    UserProfile, YaPaymentFormWithoutCash)
from orders.models import Order, OrderStatus


class UserProfileView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account:login')
    template_name = 'pages/frontend/registration/index.html'


class RegistrationView(FormView):
    """
    Форма регистрации.
    """
    form_class = RegistrationForm
    company_form = CompanyRegistrationForm
    success_url = reverse_lazy('index')
    template_name = 'pages/frontend/registration/registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'company_form': self.get_company_form(),
        })
        return context

    def get_company_form(self, form_class=None):
        return self.company_form(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        company_form = self.get_company_form()
        if form.is_valid():
            if form.cleaned_data['user_type'] == '2':
                if company_form.is_valid():
                    return self.form_valid(form, company_form)
            else:
                return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form, company_form=None):
        user = form.save()
        user.first_name = form.cleaned_data.get('fio')

        if company_form:
            company_data = company_form.cleaned_data
            user.company = company_data.get('company_name')
            user.company_address = company_data.get('company_address')
            user.inn = company_data.get('inn')
            user.is_wholesaler = True

        user.save()
        login(self.request, user)
        return super().form_valid(form)


class UpdateProfileView(LoginRequiredMixin, FormView):
    """
    Форма редактирования пользовательских данных.
    """
    login_url = reverse_lazy('account:login')
    form_class = UserProfile
    company_form = CompanyRegistrationForm
    success_url = reverse_lazy('account:index')
    template_name = 'pages/frontend/registration/edit.html'

    def get_initial(self):
        user = self.request.user

        data_mapping = {
            'fio': user.first_name,
            'phone': user.phone,
            'email': user.email,
            'user_type': 2 if user.is_wholesaler else 1,
            'company_name': user.company,
            'inn': user.inn,
            'company_address': user.company_address,
            'create_order': self.request.GET.get('create_order'),
        }

        return data_mapping.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'company_form': self.get_company_form(),
        })
        return context

    def get_company_form(self, form_class=None):
        return self.company_form(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        company_form = self.get_company_form()
        if form.is_valid():
            if form.cleaned_data['user_type'] == '2':
                if company_form.is_valid():
                    return self.form_valid(form, company_form)
            else:
                return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form, company_form=None):
        user = self.request.user
        user_data = form.cleaned_data

        user.email = user_data['email']
        user.first_name = user_data['fio']
        user.phone = user_data['phone']

        if company_form:
            company_data = company_form.cleaned_data

            user.company = company_data['company_name']
            user.company_address = company_data['company_address']
            user.inn = company_data['inn']
            user.is_wholesaler = True

        else:
            user.is_wholesaler = False

        user.save()

        if user_data['create_order'] is True:
            self.success_url = reverse('account:cart')

        return super().form_valid(form)


class PasswordRecoveryView(Recover):
    """
    Восстановление пароля.
    """
    email_template_name = 'pages/frontend/password/recovery_email.txt'
    success_url_name = 'account:password_recovery_done'
    template_name = 'pages/frontend/password/recovery.html'


class PasswordRecoveryDoneView(RecoverDone):
    """
    Восстановление пароля.
    """
    template_name = 'pages/frontend/password/recovery_done.html'


class PasswordResetView(Reset):
    """
    Восстановление пароля.
    """
    template_name = 'pages/frontend/password/reset.html'
    success_url = reverse_lazy('account:login')


class UserLoginView(LoginView):
    """
    Форма авторизации.
    """
    template_name = 'pages/frontend/registration/login.html'


class UserLogoutView(LogoutView):
    """
    Выход пользователя.
    """
    next_page = reverse_lazy('index')

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        cart = request.session.get(CART_KEY)
        auth_logout(request)
        if cart is not None:
            request.session[CART_KEY] = cart
        next_page = self.get_next_page()
        if next_page:
            return HttpResponseRedirect(next_page)
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class CartView(LoginRequiredMixin, FormView):
    """
    Страница корзины.
    """
    login_url = reverse_lazy('account:login')
    form_class = ItemFormSet
    order_form = OrderForm
    success_url = reverse_lazy('account:cart')
    template_name = 'pages/frontend/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'order_form': self.get_order_form(),
        })
        return context

    def get_form_kwargs(self):
        kwargs = {
            'order': Order.get_cart(self.request.user),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs

    def get_order_form(self, form_class=None):
        kwargs = {
            'instance': Order.get_cart(self.request.user),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
            })
        return self.order_form(**kwargs)

    def validate_user(self):
        user = self.request.user

        attrs = ['first_name']
        if user.is_wholesaler:
            attrs += ['phone', 'company', 'inn', 'company_address']

        for attr in attrs:
            if not getattr(user, attr, None):
                return False

        return True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        order_form = self.get_order_form()
        if form.is_valid():
            return self.form_valid(form, order_form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, order_form=None):
        if order_form and order_form.is_valid():
            form.order.comment = order_form.cleaned_data['comment']

        data = self.get_form_kwargs().get('data')
        if data:
            if '_submit' in data:
                if not self.validate_user():
                    form.save()
                    param = '?create_order=true'
                    self.success_url = reverse('account:profile') + param
                    return super().form_valid(form)

                if form.order.items.all():
                    form.order.created = timezone.now()
                    form.order.status = OrderStatus.INWORK
                    form.order.save()
                    self.send_mail(form)
                self.success_url = reverse('account:history_detail',
                                           kwargs={'pk': form.order.pk})

            elif '_reset' in data:
                form.order.items.all().delete()
                form.order.save()
                self.success_url = reverse('index')

        form.order.save()
        form.save()
        return super().form_valid(form)

    def send_mail(self, form):
        user = form.order.user

        if user.is_wholesaler:
            email_address = settings.EMAIL_OPT
        else:
            return True

        body_html = render_to_string(
            'orders/mail_order.html',
            {
                'items': form.order.items.all(),
                'order': form.order,
                'site': self.request.get_host(),
                'user': user,
            }
        )

        email = create_email(
            'Заказ с сайта',
            body_html,
            email_address
        )

        email.send()


class HistoryListView(LoginRequiredMixin, ListView):
    """
    Страница истории заказов.
    """
    login_url = reverse_lazy('account:login')
    model = Order
    template_name = 'pages/frontend/history.html'

    def get_queryset(self):
        request = self.request
        qs = (Order.objects
                   .filter(user=request.user)
                   .exclude(status=OrderStatus.NOT_CREATED)
                   .order_by('-created'))
        return qs


class HistoryDetailView(LoginRequiredMixin, DetailView):
    """
    Подробный просмотр заказа.
    """
    login_url = reverse_lazy('account:login')
    form_class = YaPaymentFormWithoutCash
    form_initial = None
    model = Order
    template_name = 'pages/frontend/history_detail.html'

    def get_queryset(self):
        """
        Показывать только заказы пользователя.
        """
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Добавим форму оплаты.
        """
        cart = Cart(self.request)
        user = cart.request.user
        order = kwargs.get('object', self.get_object())
        can_pay = order.status in [OrderStatus.INWORK]

        kwargs['can_pay'] = not user.is_wholesaler and can_pay
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)

    def get_form(self, **kwargs):
        """
        Получаем форму оплаты.
        """
        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """
        Передаём данные для создания формы оплаты.
        """
        kwargs = {}
        if self.request.method == 'GET':
            order = self.get_object()
            kwargs['initial'] = {
                'phone': self.request.user.phone,
                'email': self.request.user.email,
                'delivery_type': order.delivery_type,
                'delivery_address': order.delivery_address,
                'zip_code': order.zip_code,
                'weight': order.weight,
            }
        elif self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form and form.is_valid():
            success_url = form.create_payment(request=request,
                                              order=self.object,
                                              payer=request.user)
            return HttpResponseRedirect(success_url)
        else:
            context = self.get_context_data(object=self.object, form=form)
            return self.render_to_response(context)


class SuccessPageView(TemplateView):
    """
    Страница "Спасибо за заявку".
    """
    template_name = 'pages/frontend/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'order': self.get_order(),
        })
        return context

    def get_order(self):
        """
        Получить оплаченные заказ клиента.
        """
        payer = self.request.user
        order_id = self.request.GET.get('orderId')
        try:
            return Order.objects.get(
                pk=order_id, user=payer, status=OrderStatus.CONFIRMED)
        except Order.DoesNotExist:
            return None
