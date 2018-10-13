from django.views.generic import FormView

from yandex_kassa.forms import BasePaymentForm


class TestFormView(FormView):
    form_class = BasePaymentForm
    template_name = 'yandex_kassa/test.html'

    def form_valid(self, form):
        form.create_payment()
        return super().form_valid(form)
