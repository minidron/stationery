from odinass.models import Category

from orders.models import Order


def menu(request):
    user = request.user
    categories = Category.objects.root_nodes().filter(is_published=True)

    return {
        'categories': categories,
        'cart': Order.get_cart(user) if not user.is_anonymous else None,
    }
