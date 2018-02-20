from django.contrib.auth.views import LoginView, LogoutView
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lib.email import create_email

from orders.forms import ItemFormSet
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


class UserLoginView(LoginView):
    template_name = 'pages/frontend/registration/login.html'


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('index')


class CartView(FormView):
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
            }
        )

        email = create_email(
            'Заказ с сайта',
            body_html,
            'opt@kancmiropt.ru'
        )

        email.send()


class HistoryListView(ListView):
    model = Order
    template_name = 'pages/frontend/history.html'
    ordering = ['-created']
    queryset = Order.objects.exclude(status=OrderStatus.NOT_CREATED)


class HistoryDetailView(DetailView):
    model = Order
    template_name = 'pages/frontend/history_detail.html'
