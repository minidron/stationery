from django.views.generic import DetailView, TemplateView

from pages.models import Page

from odinass.models import Category, Offer


class IndexView(TemplateView):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'hot': Offer.objects.all()[:8],
        })
        return context


class CatalogView(TemplateView):
    template_name = 'pages/catalog.html'


class CategoryView(DetailView):
    model = Category
    template_name = 'pages/category.html'


class ProductView(DetailView):
    model = Offer
    template_name = 'pages/product.html'


class PageView(DetailView):
    model = Page
    template_name = 'pages/static.html'
