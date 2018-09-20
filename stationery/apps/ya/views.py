from django.conf import settings
from django.views.generic import FormView

from yandex_money.forms import PaymentForm

from yandex_money.models import Payment

from orders.models import Order


class OrderView(FormView):
    form_class = PaymentForm
    template_name = 'ya/order.html'

    def get_payment_instance(self, order=None):
        """
        Создаём объект "Платёж".
        """
        site_url = '%s://%s' % (self.request.scheme, self.request.get_host())

        if not order:
            order_pk = self.request.GET.get('order')
            order = Order.objects.get(pk=order_pk)

        payment = Payment(
            user=self.request.user,
            order_amount=order.remaining_payment_sum,
            success_url='%s%s' % (site_url, settings.YANDEX_MONEY_SUCCESS_URL),
            fail_url='%s%s' % (site_url, settings.YANDEX_MONEY_FAIL_URL),
            article_id=order.pk,
        )

        payment.save()

        return payment

    def get_form_kwargs(self):
        """
        Добавляем "Платеж" в форму.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.get_payment_instance(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form_action': settings.YANDEX_MONEY_ENDPOINT,
        })
        return context
