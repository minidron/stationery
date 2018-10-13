import uuid

from django import forms

from yandex_checkout import Payment

from yandex_kassa.conf import settings as kassa_settings
from yandex_kassa.models import PaymentMethod


class BasePaymentForm(forms.Form):
    """
    Базовый класс для платёжной формы.
    """
    error_css_class = 'error'
    required_css_class = 'required'

    payment_method_data = forms.ChoiceField(
        label='Способ оплаты', choices=PaymentMethod.CHOICES)
    phone = forms.CharField(
        label='Телефон', required=False)
    email = forms.EmailField(
        label='Email', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_payment_method_choices()

    def clean(self):
        cleaned_data = super().clean()
        self.validating_payment_method(cleaned_data)
        return cleaned_data

    def set_payment_method_choices(self):
        """
        Указываем список методов оплат согласно настройкам.
        """
        payment_methods = kassa_settings.PAYMENT_METHOD
        field = self.fields['payment_method_data']

        f_choices = filter(lambda x: x[0] in payment_methods,
                           field.widget.choices)
        s_choices = sorted(f_choices,
                           key=lambda x: payment_methods.index(x[0]))

        field.widget.choices = s_choices
        field.initial = kassa_settings.PAYMENT_DEFAULT_METHOD

    def validating_payment_method(self, cleaned_data):
        """
        Проверяем, всех ли данных хватает, чтоб произвести оплату.
        """
        payment_method = cleaned_data['payment_method_data']
        phone = cleaned_data['phone']

        if payment_method in [PaymentMethod.MOBILE_BALANCE,
                              PaymentMethod.QIWI] and not phone:
            msg = 'Для этого способа оплаты требуется указать номер телефона'
            self.add_error('phone', msg)

    def create_payment(self):
        import ipdb; ipdb.set_trace()
