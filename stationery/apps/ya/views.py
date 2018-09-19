from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.views.generic import FormView

from yandex_money.forms import PaymentForm

from yandex_money.models import Payment

from orders.models import Order


class YandexPaymentForm(PaymentForm):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs['instance']
        super().__init__(*args, **kwargs)


class HttpResponseTemporaryRedirect(HttpResponse):
    status_code = 307

    def __init__(self, redirect_to):
        HttpResponse.__init__(self)
        self['Location'] = iri_to_uri(redirect_to)


class OrderView(FormView):
    form_class = YandexPaymentForm
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
            order_amount=order.amount,
            success_url='%s%s' % (site_url, settings.YANDEX_MONEY_SUCCESS_URL),
            fail_url='%s%s' % (site_url, settings.YANDEX_MONEY_FAIL_URL),
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

    def form_valid(self, form):
        form.instance.save()
        url = 'https://demomoney.yandex.ru/eshop.xml'
        return HttpResponseTemporaryRedirect(url)
