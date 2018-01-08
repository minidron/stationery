from django import forms
from django.db.models import Count, IntegerField, Case, Max, Min, Q, When
from django.views.generic import DetailView, ListView, TemplateView

from pages.models import Page

from odinass.models import Category, Offer, Price, Property, SalesType


class TestView(TemplateView):
    template_name = 'pages/frontend/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(level=0)[1:4]
        context.update({
            'categories': categories,
        })
        return context


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
    paginate_by = 15
    allow_empty = ListView.allow_empty
    get_allow_empty = ListView.get_allow_empty
    get_paginate_by = ListView.get_paginate_by
    get_paginate_orphans = ListView.get_paginate_orphans
    get_paginator = ListView.get_paginator
    page_kwarg = ListView.page_kwarg
    paginate_orphans = ListView.paginate_orphans
    paginate_queryset = ListView.paginate_queryset
    paginator_class = ListView.paginator_class
    template_name = 'pages/frontend/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = context['category']
        offers = category.offers

        page_size = self.get_paginate_by(offers)
        if page_size:
            paginator, page, offers, is_paginated = self.paginate_queryset(
                offers, page_size)
            context.update({
                'is_paginated': is_paginated,
                'page_kwarg': self.page_kwarg,
                'page_obj': page,
                'paginator': paginator,
            })

        context.update({
            'offers': offers,
        })
        return context


class ProductView(DetailView):
    model = Offer
    template_name = 'pages/product.html'


class PageView(DetailView):
    model = Page
    template_name = 'pages/static.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = (Category.objects
                            .get(pk='43ea0da8-ad21-11db-a2b2-00c09fa8f069'))

        context.update({
            'category': category,
        })
        return context
