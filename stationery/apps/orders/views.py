from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lib.email import create_email

from orders.forms import CompanyRegistrationForm, ItemFormSet, RegistrationForm
from orders.models import Order, OrderStatus


class OrderAPIView(APIView):
    """
    API для заказов.
    """
    def get(self, request, *args, **kwargs):
        order = Order.get_cart(request.user)
        return Response({'amount': order.amount}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        order = Order.get_cart(request.user)
        quantity = int(request.POST['quantity'])
        order.add_item(request.POST['offer'], quantity, user=request.user)
        return Response({'amount': order.amount}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        order = Order.get_cart(request.user)
        offer = request.POST['offer']
        order.remove_item(offer)
        return Response({'amount': order.amount}, status=status.HTTP_200_OK)


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


class CartView(FormView):
    """
    Страница корзины.
    """
    form_class = ItemFormSet
    success_url = reverse_lazy('cart')
    template_name = 'pages/frontend/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

    def form_valid(self, form):
        data = self.get_form_kwargs().get('data')
        if data:
            if '_submit' in data:
                form.order.status = OrderStatus.INWORK
                form.order.save()
                self.send_mail(form)
                self.success_url = reverse('index')

            if '_reset' in data:
                form.order.items.all().delete()
                form.order.save()
                self.success_url = reverse('index')
        form.save()
        return super().form_valid(form)

    def send_mail(self, form):
        body_html = render_to_string(
            'orders/mail_order.html',
            {
                'site': self.request.get_host(),
                'order': form.order,
                'items': form.order.items.all(),
                'request': self.request,
            }
        )

        email = create_email(
            'Заказ с сайта',
            body_html,
            'opt@kancmiropt.ru'
        )

        email.send()


class HistoryListView(ListView):
    """
    Страница истории заказов.
    """
    model = Order
    template_name = 'pages/frontend/history.html'

    def get_queryset(self):
        request = self.request
        qs = (Order.objects
                   .filter(user=request.user)
                   .exclude(status=OrderStatus.NOT_CREATED)
                   .order_by('-created'))
        return qs


class HistoryDetailView(DetailView):
    """
    Подробный просмотр заказа.
    """
    model = Order
    template_name = 'pages/frontend/history_detail.html'
