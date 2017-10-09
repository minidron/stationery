from django.urls import reverse

from odinass.models import Category

from pages.models import Page


def menu(request):
    categories = Category.objects.root_nodes().values('title', 'pk')
    pages = Page.objects.values('title', 'icon', 'slug')

    return {
        'top_nav': [
            {
                'title': 'Каталог товаров',
                'url': '#',
                'image': None,
                'childs': [{
                    'title': category['title'],
                    'url': reverse('pages:category', args=[category['pk']]),
                    'image': None,
                } for category in categories],
            }
        ] + [{
            'title': page['title'],
            'url': page['slug'],
            'icon': page['icon'],
            'image': None,
        } for page in pages]
    }
