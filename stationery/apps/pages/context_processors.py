from odinass.models import Category


def menu(request):
    categories = Category.objects.root_nodes()

    return {
        'categories': categories,
    }
