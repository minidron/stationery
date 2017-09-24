from odinass.models import Category


def menu(request):
    categories = Category.objects.root_nodes().values('title')
    return {
        'top_nav': [
            {
                'title': 'Каталог товаров',
                'url': '#',
                'image': None,
                'childs': [{
                    'title': category['title'],
                    'url': '#',
                    'image': None,
                } for category in categories],
            }
        ]
    }
