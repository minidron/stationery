from orders import models as orders_models


CART_ID = '_cart_id'


class Cart(object):
    """
    Корзина товаров.
    """
    def __init__(self, request):
        cart_id = request.session.get(CART_ID)
        if cart_id:
            try:
                cart = orders_models.Cart.objects.get(
                    profile=request.user.profile, is_complete=False)
            except orders_models.Cart.DoesNotExist:
                cart = self.new(request)
        else:
            cart = self.new(request)
        self.cart = cart

    def new(self, request):
        cart = orders_models.Cart(profile=request.user.profile)
        cart.save()
        request.session[CART_ID] = cart.id
        return cart
