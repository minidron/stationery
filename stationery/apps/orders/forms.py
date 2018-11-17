from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.functional import cached_property

from yandex_kassa.conf import settings as kassa_settings
from yandex_kassa.forms import BasePaymentForm
from yandex_kassa.models import PaymentMethod

from orders.models import Item, Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['comment']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('quantity', )
        widgets = {
            'quantity': forms.TextInput,
        }

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        limit = self.instance.offer.rest_limit
        if limit < data:
            raise forms.ValidationError('Осталось %s шт.' % limit)
        return data


class ItemFormSet(object):
    """
    Формсет для товаров в корзине.
    """
    def __init__(self, data=None, order=None):
        self.data = data or {}
        self.order = order

    def __iter__(self):
        return iter(self.forms)

    def __getitem__(self, index):
        if self.forms:
            return self.forms[index]

    @cached_property
    def forms(self):
        """
        Формируем формы товаров.
        """
        forms = []
        for item in self.order.items.select_related('offer').all():
            defaults = {
                'data': self.data or None,
                'prefix': self.add_prefix(item.id),
                'instance': item,
            }

            form = ItemForm(**defaults)
            forms.append(form)
        return forms

    def add_prefix(self, index):
        return 'form-%s' % (index)

    def is_valid(self):
        """
        Проверяем все формы на валидность, пропуская формы, которые будут
        удалены, а также если форма не была изменена
        """
        status = []
        for form in self:
            is_valid = form.is_valid()
            if form.has_changed():
                status.append(is_valid)
        return all(status)

    def save(self):
        """
        Сохраняем измененные формы или удаляем, если форма была выбрана на
        удаление
        """
        for form in self:
            if form.has_changed():
                form.save()


class RegistrationForm(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'

    fio = forms.CharField(
        label='ФИО',
        required=True)
    phone = forms.CharField(
        label='Телефон',
        required=True)
    email = forms.EmailField(
        label='E-mail',
        required=False)
    user_type = forms.ChoiceField(
        label='Тип пользователя',
        required=True,
        choices=((1, 'физическое лицо'), (2, 'юридическое лицо')),
        widget=forms.RadioSelect())


class CompanyRegistrationForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    company_name = forms.CharField(
        label='Наименование организации',
        required=True)
    inn = forms.IntegerField(
        label='ИНН',
        required=True, min_value=1000000000)
    company_address = forms.CharField(
        label='Юридический адрес',
        required=True,
        widget=forms.Textarea())


class UserProfile(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    fio = forms.CharField(
        label='ФИО',
        required=True)
    phone = forms.CharField(
        label='Телефон',
        required=True)
    email = forms.EmailField(
        label='E-mail',
        required=False)
    user_type = forms.ChoiceField(
        label='Тип пользователя',
        required=True,
        choices=((1, 'физическое лицо'), (2, 'юридическое лицо')),
        widget=forms.RadioSelect())

    # Проверка при создании заказа, что пользователь не заполнил все поля.
    create_order = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=False)


class YaPaymentForm(BasePaymentForm):
    payment_method_data = forms.ChoiceField(
        label='Способ оплаты',
        widget=forms.RadioSelect(), choices=PaymentMethod.CHOICES)

    def get_payment_amount(self):
        return {
            'amount': {
                'value': self.order.amount,
                'currency': kassa_settings.PAYMENT_DEFAULT_CURRENCY,
            }
        }

    def get_payment_method_data(self):
        return {
            'payment_method_data': {
                'type': self.cleaned_data['payment_method_data'],
            }
        }

    def get_payment_confirmation(self):
        return {
            'confirmation': {
                'type': 'redirect',
                'return_url': self.request.build_absolute_uri(),
            }
        }

    def get_payment_description(self):
        return {'description': str(self.order)}

    def get_payment_data(self, payment_data):
        data = super().get_payment_data(payment_data)
        data.update({
            'order_id': str(self.order.pk),
            'payer': self.payer,
            'payer_phone': self.cleaned_data['phone'],
            'payer_email': self.cleaned_data['email'],
        })
        return data

    def create_payment(self, request, order=None, payer=None):
        self.request = request
        return super().create_payment(order, payer)
