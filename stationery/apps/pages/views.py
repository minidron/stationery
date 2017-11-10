from django import forms
from django.db.models import IntegerField, Case, Max, Min, Q, When
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

        offers = (Offer.objects
                       .select_related('product')
                       .filter(product__categories=category))

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

        search_params = {}

        if prices['price__min'] and prices['price__max']:
            context['price__min'] = int(prices['price__min'])
            context['price__max'] = int(prices['price__max'])

            if form_search.is_valid():
                offers = offers.annotate(
                    retail_price=Case(
                        When(prices__price_type__sales_type=SalesType.RETAIL,
                             then='prices__price'),
                        output_field=IntegerField(),
                    ))

                data = form_search.cleaned_data
                filter_price = (
                    Q(retail_price__gte=data['minCost']) &
                    Q(retail_price__lte=data['maxCost']))

        result = offers.filter(filter_price, **search_params)
        context.update({
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
