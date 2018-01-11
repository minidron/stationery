import collections

from django import forms
from django.db.models import Count, Max, Min, Prefetch
from django.views.generic import DetailView, ListView, TemplateView

from pages.models import Page

from odinass.models import Category, Offer, Property, PropertyValue


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
    # template_name = 'pages/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = context['category']
        offers = category.offers
        prices = offers.aggregate(Min('retail_price'), Max('retail_price'))

        property_values = Prefetch(
            'property_values',
            queryset=(PropertyValue.objects
                                   .filter(products__categories=category)
                                   .distinct()))

        properties = (
            Property.objects
                    .filter(property_values__products__offers__in=offers)
                    .prefetch_related(property_values)
                    .order_by('title')
                    .distinct())

        # Форма поиска
        form_search = self.get_search_form(properties)(
            self.request.GET or None)

        # Фильтрация
        if form_search.is_valid():
            data = form_search.cleaned_data

            filter_properties = []
            for param_key, param_value in data.items():
                if param_value and param_key not in ['minCost', 'maxCost']:
                    if isinstance(param_value, list):
                        filter_properties += param_value
                    else:
                        filter_properties.append(param_value)

            if filter_properties:
                offers = (
                    offers.filter(
                              product__property_values__in=filter_properties)
                          .annotate(
                              num_tags=Count('product__property_values'))
                          .filter(num_tags=len(filter_properties)))

        # Пагинация
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
            'prices': prices,
            'offers': offers,
            'form_search': form_search,
        })
        return context

    def get_search_form(self, properties):
        fields = collections.OrderedDict()

        fields.update({
            'minCost': forms.IntegerField(required=False),
            'maxCost': forms.IntegerField(required=False),
        })

        for prop in properties:
            choices = [
                (prop_value.pk, prop_value.title)
                for prop_value in prop.property_values.all()]
            fields[str(prop.pk)] = forms.MultipleChoiceField(
                label=prop.title, required=False,
                choices=self.sort_choices(choices),
                widget=forms.CheckboxSelectMultiple)

        SearchForm = type('SearchForm', (forms.BaseForm, ),
                          {'base_fields': fields})
        return SearchForm

    def sort_choices(self, choices):
        num_list = []
        str_list = []
        for val, title in choices:
            try:
                title = title.replace(',', '.')
                title = float(title)
                if title.is_integer():
                    title = int(title)
                num_list.append((val, title))
            except ValueError:
                str_list.append((val, title))
        num_list = sorted(num_list, key=lambda tup: tup[1])
        str_list = sorted(str_list, key=lambda tup: tup[1])
        return num_list + str_list


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
