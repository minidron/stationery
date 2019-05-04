from django.views.generic import FormView

from cart.cart import Cart
from cart.forms import CartItemFormSet


class CartView(FormView):
    """
    Страница корзины.
    """
    form_class = CartItemFormSet
    template_name = 'cart/cart.html'

    def get_form_kwargs(self):
        kwargs = {
            'cart': Cart(self.request),
        }
        return kwargs
