from django import forms


class CartItemForm(forms.Form):
    quantity = forms.IntegerField()

    def __init__(self, offer, *args, **kwargs):
        self.offer = offer
        super().__init__(*args, **kwargs)


class CartItemFormSet:
    """
    Формсет для товаров в корзине.
    """
    def __init__(self, data=None, cart=None, *args, **kwargs):
        self.data = data or {}
        self.cart = cart

    def __iter__(self):
        return iter(self.forms)

    def __getitem__(self, index):
        if self.forms:
            return self.forms[index]

    @property
    def forms(self):
        """
        Формируем формы товаров.
        """
        forms = []
        for item in self.cart:
            defaults = {
                'data': self.data or None,
                'prefix': self.add_prefix(item['instance'].id),
                'offer': item['instance'],
                'initial': {
                    'quantity': item['quantity'],
                },
            }

            form = CartItemForm(**defaults)
            forms.append(form)
        return forms

    def add_prefix(self, index):
        return 'form-%s' % (index)

    def is_valid(self):
        """
        Проверяем все формы на валидность.
        """
        status = []
        for form in self:
            is_valid = form.is_valid()
            status.append(is_valid)
        return all(status)
