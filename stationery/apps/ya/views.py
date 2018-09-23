from django.views.generic import RedirectView

from yandex_money.models import Payment

from orders.models import Order


class SuccessPayment(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = '/'
        order_number = self.request.GET.get('orderNumber')
        if order_number:
            payment = Payment.objects.get(order_number=order_number)
            order = Order.objects.get(pk=payment.article_id)
            url = order.get_absolute_url()
        return url
