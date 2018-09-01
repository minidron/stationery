from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.functional import cached_property

from orders.models import Order, Item


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('quantity', )
        widgets = {
            'quantity': forms.TextInput,
        }


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
