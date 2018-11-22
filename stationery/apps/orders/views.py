from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, TemplateView

from lib.email import create_email

from orders.forms import (CompanyRegistrationForm, ItemFormSet, OrderForm,
                          RegistrationForm, UserProfile, YaPaymentForm)
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

        user_data = form.cleaned_data
        user.email = user_data.get('email')
        user.first_name = user_data.get('fio')
        user.profile.phone = user_data.get('phone')

        if company_form:
            company_data = company_form.cleaned_data
            user.profile.company = company_data.get('company_name')
            user.profile.company_address = company_data.get('company_address')
            user.profile.inn = company_data.get('inn')

            group = Group.objects.get(name='Оптовик')
            group.user_set.add(user)
            user.profile.save()
            user.save()

        username = user_data.get('username')
        raw_password = user_data.get('password1')
        user = authenticate(username=username, password=raw_password)
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
        is_opt = user.groups.filter(name='Оптовик').exists()

        data_mapping = {
            'fio': user.first_name,
            'phone': user.profile.phone,
            'email': user.email,
            'user_type': 2 if is_opt else 1,
            'company_name': user.profile.company,
            'inn': user.profile.inn,
            'company_address': user.profile.company_address,
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
        group = Group.objects.get(name='Оптовик')

        user.email = user_data['email']
        user.first_name = user_data['fio']
        user.profile.phone = user_data['phone']

        if company_form:
            company_data = company_form.cleaned_data

            user.profile.company = company_data['company_name']
            user.profile.company_address = company_data['company_address']
            user.profile.inn = company_data['inn']

            group.user_set.add(user)
            user.profile.save()

        else:
            group.user_set.remove(user)

        user.save()

        if user_data['create_order'] is True:
            self.success_url = reverse('account:cart')

        return super().form_valid(form)


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
        is_opt = user.groups.filter(name='Оптовик').exists()

        attrs = ['first_name']
        profile_attrs = ['phone']
        if is_opt:
            profile_attrs += ['company', 'inn', 'company_address']

        for attr in attrs:
            if not getattr(user, attr, None):
                return False

        for attr in profile_attrs:
            if not getattr(user.profile, attr, None):
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
                self.success_url = reverse('account:history')

            elif '_reset' in data:
                form.order.items.all().delete()
                form.order.save()
                self.success_url = reverse('index')

        form.order.save()
        form.save()
        return super().form_valid(form)

    def send_mail(self, form):
        user = form.order.user

        if user.groups.filter(name='Оптовик'):
            email_address = settings.EMAIL_OPT
        else:
            email_address = settings.EMAIL_PRIVATE

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
    form_class = YaPaymentForm
    form_initial = None
    model = Order
    template_name = 'pages/frontend/history_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = {}
        if self.request.method == 'GET':
            kwargs['initial'] = {
                'phone': self.request.user.profile.phone,
                'email': self.request.user.email,
            }
        elif self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST
        return kwargs

    def get_form(self, **kwargs):
        form = None
        groups = self.request.user.groups
        if not groups.filter(name='Оптовик'):
            order = self.object
            if order.status in [OrderStatus.CONFIRMED, OrderStatus.INWORK]:
                form = self.form_class(**self.get_form_kwargs())
        return form

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)

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
