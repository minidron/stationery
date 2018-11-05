from django import forms

from yandex_kassa.conf import settings as kassa_settings
from yandex_kassa.interface import YandexKassaInterface
from yandex_kassa.models import Payment, PaymentMethod


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

    def get_payment_amount(self):
        """
        Возвращает dict `amount`.
        """
        raise NotImplementedError(
                'Необходимо определить get_payment_amount() в `%s`.' %
                type(self).__name__)

    def get_payment_description(self):
        """
        Возвращает dict `description`.
        """
        return None

    def get_payment_confirmation(self):
        """
        Возвращает dict `confirmation`.
        """
        raise NotImplementedError(
                'Необходимо определить get_payment_confirmation() в `%s`.' %
                type(self).__name__)

    def get_payment_method_data(self):
        """
        Возвращает dict `payment_method_data`.
        """
        raise NotImplementedError(
                'Необходимо определить get_payment_method_data() в `%s`.' %
                type(self).__name__)

    def get_payment_receipt(self):
        """
        Возвращает dict `receipt`.
        """
        return None

    def get_payment_data(self, payment_data):
        """
        Возвращает dict с полями модели `Payment`.
        """
        return payment_data

    def create_payment(self, order=None, payer=None):
        """
        Создаёт платёж.

        Подробнее про параметры, при создании платежа:
        https://kassa.yandex.ru/docs/checkout-api/#sozdanie-platezha
        """
        self.order = order
        self.payer = payer

        data = {'capture': True,
                **self.get_payment_amount(),
                **self.get_payment_method_data(),
                **self.get_payment_confirmation()}

        for method in ['get_payment_description', 'get_payment_receipt']:
            additional_data = getattr(self, method)()
            if additional_data:
                data.update(additional_data)

        interface = YandexKassaInterface()
        payment_data = interface.create_payment(data)
        success_url = payment_data.pop('confirmation_url')
        Payment.objects.create(**self.get_payment_data(payment_data))

        return success_url
