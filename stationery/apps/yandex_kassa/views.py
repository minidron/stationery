from django.views.generic import FormView

from yandex_kassa.forms import YandexPaymentForm


class TestFormView(FormView):
    form_class = YandexPaymentForm
    template_name = 'yandex_kassa/test.html'

    def form_valid(self, form):
        self.success_url = form.create_payment()
        return super().form_valid(form)
