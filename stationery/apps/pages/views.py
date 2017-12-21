from django import forms
from django.db.models import Count, IntegerField, Case, Max, Min, Q, When
from django.views.generic import DetailView, TemplateView

from pages.models import Page

from odinass.models import Category, Offer, Price, Property, SalesType


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = context['category']

        offers = category.offers

        prices = (Price.objects
                       .filter(offer__in=offers,
                               price_type__sales_type=SalesType.RETAIL)
                       .aggregate(Min('price'), Max('price')))

        properties = (
            Property.objects
                    .filter(property_values__products__categories=category)
                    .distinct())

        form_search = self.get_search_form(properties)(
            self.request.GET or None)

        if prices['price__min'] and prices['price__max']:
            context['price__min'] = int(prices['price__min'])
            context['price__max'] = int(prices['price__max'])

        result = offers
        if form_search.is_valid():
            data = form_search.cleaned_data
            result = result.annotate(
                retail_price=Case(
                    When(prices__price_type__sales_type=SalesType.RETAIL,
                         then='prices__price'),
                    output_field=IntegerField(),
                ))

            filter_prices = (
                Q(retail_price__gte=data['minCost']) &
                Q(retail_price__lte=data['maxCost']))
            result = result.filter(filter_prices)

            filter_properties = []
            for param_key, param_value in data.items():
                if param_value and param_key not in ['minCost', 'maxCost']:
                    filter_properties.append(param_value)

            if filter_properties:
                result = (result.filter(
                        product__property_values__in=filter_properties)
                                .annotate(
                                    num_tags=Count('product__property_values'))
                                .filter(num_tags=len(filter_properties)))

        context.update({
            'test_offers': offers,
            'offers': result,
            'properties': properties,
            'form_search': form_search,
        })

        return context

    def get_search_form(self, properties):
        fields = {
            'minCost': forms.IntegerField(required=False),
            'maxCost': forms.IntegerField(required=False),
        }

        for prop in properties:
            choices = [('', '---')]
            choices += [
                (prop_value.pk, prop_value.title)
                for prop_value in prop.property_values
                                      .filter(products__categories=self.object)
                                      .distinct()]
            fields[str(prop.pk)] = forms.ChoiceField(
                label=prop.title, required=False, choices=choices)

        SearchForm = type('SearchForm', (forms.BaseForm, ),
                          {'base_fields': fields})
        return SearchForm


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
