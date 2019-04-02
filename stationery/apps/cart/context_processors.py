from cart.cart import Cart


def cart(request):
    """
    Добавляем объект `Корзина` в контекст сайта.
    """
    return {
        'cart': Cart(request)
    }
