import collections
import operator
from functools import reduce

from django import forms
from django.db.models import F, Func, Max, Min, Prefetch, Q
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView, TemplateView

from odinass.models import Category, Offer, Property, PropertyValue, Tags
from odinass.serializers import SearchOfferFilter
from orders.models import Office
from pages.models import Blog, Page, Slider


class IndexView(TemplateView):
    """
    Главная страница.
    """
    template_name = 'pages/frontend/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'favorite_offers': (Offer.objects
                                .offers(user=self.request.user)
                                .filter(product__is_favorite=True)
                                .order_by('product__order')),
            'slider_list': Slider.objects.all(),
        })
        return context


class Floor(Func):
    function = 'FLOOR'
    arity = 1


class Ceiling(Func):
    function = 'CEILING'
    arity = 1


class CategoryView(DetailView):
    """
    Страница категории.
    """
    model = Category
    slug_field = 'path'
    slug_url_kwarg = 'path'
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

    def get_object(self, queryset=None):
        """
        Показываем 404, если категория или одна из родительских категорий не
        опубликована.
        """
        if queryset is None:
            queryset = self.get_queryset()

        path = self.kwargs.get('path')
        qs = (queryset.filter(path=path)
              .get_ancestors(include_self=True)
              .filter(is_published=False))

        if len(qs) > 0:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return super().get_object(queryset=queryset)

    def get_context_data(self, **kwargs):
        stockpath = self.request.path
        context = super().get_context_data(**kwargs)
        category = context['category']
        offers = (category.offers(user=self.request.user)
                  .filter(retail_price__gt=0))
        has_offers = True
        if not offers:
            has_offers = False
        prices = offers.aggregate(
            retail_price__min=Floor(Min('retail_price')),
            retail_price__max=Ceiling(Max('retail_price')))
        order = 'title'

        property_values = Prefetch(
            'property_values',
            queryset=(PropertyValue.objects
                      .filter(products__category=category)
                      .distinct()))

        properties = (
            Property.objects
            .filter(property_values__products__offers__in=offers)
            .prefetch_related(property_values)
            .order_by('title')
            .distinct())
        properties_ids = [str(property.pk) for property in properties]

        # Форма поиска
        form_search = self.get_search_form(properties)(
            self.request.GET or None)

        # Фильтрация
        if form_search.is_valid():
            data = form_search.cleaned_data
            if data:
                context['is_filtered'] = True

            if data.get('minCost') and data.get('maxCost'):
                offers = offers.filter(
                    Q(retail_price__gte=data['minCost']) &
                    Q(retail_price__lte=data['maxCost']))

            if data.get('has_rests'):
                offers = offers.filter(rests_count__gt=0)

            for param_key, param_values in data.items():
                if param_key in properties_ids and param_values:
                    filter = reduce(
                        operator.or_,
                        [Q(product__property_values=v) for v in param_values])
                    offers = offers.filter(filter)

            if data.get('order'):
                if data.get('order') == 'aprice':
                    order = 'retail_price'
                elif data.get('order') == 'dprice':
                    order = '-retail_price'

        # Сортировка
        offers = offers.order_by(order)

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
            'has_offers': has_offers,
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
            'has_rests': forms.BooleanField(label='Есть в наличии',
                                            required=False),
            'order': forms.ChoiceField(
                label='Сортировка', required=False, choices=(
                    ('', 'нет'),
                    ('aprice', 'По возрастанию цены'),
                    ('dprice', 'По убыванию цены'),
                )),
        })

        for prop in properties:
            choices = [
                (prop_value.pk, prop_value.title)
                for prop_value in prop.property_values.all()]
            fields[str(prop.pk)] = forms.MultipleChoiceField(
                label=prop.title, required=False,
                choices=self.sort_choices(choices),
                widget=forms.CheckboxSelectMultiple)

        SearchForm = type('SearchForm', (forms.BaseForm,),
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

    def render_to_response(self, context, **response_kwargs):
        (Category.objects.filter(path=self.kwargs['path'])
         .update(views=F('views') + 1))
        return super().render_to_response(context, **response_kwargs)


class ProductView(DetailView):
    """
    Страница продукта.
    """
    model = Offer
    template_name = 'pages/frontend/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = kwargs['object']
        category = obj.product.category
        category.offers(self.request.user).filter(pk=obj.pk)

        context.update({
            'category': category,
            'offer': category.offers(self.request.user).get(pk=obj.pk),
        })
        return context


class PageView(DetailView):
    """
    Статичные страницы.
    """
    model = Page
    template_name = 'pages/frontend/static.html'


class SearchOfferView(ListView):
    """
    Поиск предложений по названию.
    """
    context_object_name = 'offers'
    model = Offer
    paginate_by = 20
    template_name = 'pages/frontend/search.html'

    def __init__(self, *args, **kwargs):
        self.categories = None
        self.order_by = None
        super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_kwarg': 'page',
        })
        offers = self.object_list
        order = self.order_by or 'title'

        prices = None
        has_offers = False

        form_search = self.get_search_form()(
            self.request.GET or None)

        if offers:
            offers = offers.filter(retail_price__gt=0)

            has_offers = True
            prices = offers.aggregate(
                retail_price__min=Floor(Min('retail_price')),
                retail_price__max=Ceiling(Max('retail_price')))

            # Фильтрация
            if form_search.is_valid():
                data = form_search.cleaned_data
                if data:
                    context['is_filtered'] = True

                if data.get('minCost') and data.get('maxCost'):
                    offers = offers.filter(
                        Q(retail_price__gte=data['minCost']) &
                        Q(retail_price__lte=data['maxCost']))

                if data.get('has_rests'):
                    offers = offers.filter(rests_count__gt=0)

                if data.get('category'):
                    offers = offers.filter(product__category=data.get('category'))

                if data.get('order'):
                    if data.get('order') == 'aprice':
                        order = 'retail_price'
                    elif data.get('order') == 'dprice':
                        order = '-retail_price'

        # Сортировка
        offers = offers.order_by(order)

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
            'has_offers': has_offers,
            'prices': prices,
            'offers': offers,
            'form_search': form_search,
            'categories': self.categories
        })
        return context

    def get_search_form(self):
        fields = collections.OrderedDict()

        fields.update({
            'q': forms.CharField(widget=forms.HiddenInput()),
            'category': forms.ModelChoiceField(queryset=self.categories,
                                               required=False,
                                               widget=forms.HiddenInput()),
            'minCost': forms.IntegerField(required=False),
            'maxCost': forms.IntegerField(required=False),
            'has_rests': forms.BooleanField(label='Есть в наличии',
                                            required=False),
            'order': forms.ChoiceField(
                label='Сортировка', required=False, choices=(
                    ('', 'нет'),
                    ('aprice', 'По возрастанию цены'),
                    ('dprice', 'По убыванию цены'),
                )),
        })

        SearchForm = type('SearchForm', (forms.BaseForm,),
                          {'base_fields': fields})
        return SearchForm

    def get_queryset(self):
        qs = Offer.objects.none()
        if self.request.GET:
            filter = SearchOfferFilter(self.request.GET)
            filter.qs  # обращение к этому свойству запускает все фильтры из сета
            ids = filter.filters['q'].hits_list  # queryset, возвращаемый фильтром, тут не нужен, только хиты
            if ids:
                self.order_by = filter.filters['q'].hits_order
                self.categories = Category.objects.filter(
                    products__offers__id__in=ids).distinct()
                qs = Offer.objects.offers(user=self.request.user, ids=ids)
        return qs


class OfficeListView(ListView):
    """
    Вью для списка модели `Офис`.
    """
    model = Office
    template_name = 'pages/frontend/contact.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_published=True)


class BlogListView(ListView):
    """
    Страница списка блога `Мастер-классы`.
    """
    model = Blog
    template_name = 'pages/frontend/blog_list.html'


class BlogDetailView(DetailView):
    """
    Страница просмотра записи блога `Мастер-классы`.
    """
    model = Blog
    template_name = 'pages/frontend/blog.html'


def catalog_view(request, *args, **kwargs):
    path = kwargs['path']
    if Category.objects.filter(path=path).exists():
        return CategoryView.as_view()(request, *args, **kwargs)
    else:
        slugs = path.split('/')
        category_path = '/'.join(slugs[:-1])
        slug = slugs[-1]
        new_kwargs = {'category_path': category_path, 'slug': slug}
        return ProductView.as_view()(request, *args, **new_kwargs)


class TagsView(TemplateView):
    """ Вьюха генерящая выборку товаров по тегу """
    template_name = 'pages/frontend/category_tags.html'

    def get(self, request, *args, **kwargs):
        tag = request.GET.get('tag')
        kwargs['tag'] = tag
        context = self.get_context_data(**kwargs)
        tags_title = Tags.objects.filter(tegs=tag).first()
        if tags_title:
            context['tags_title'] = tags_title
            return self.render_to_response(context)
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'favorite_offers': (Offer.objects
                                .offers(user=self.request.user)
                                .filter(offer_tags__tegs=kwargs['tag'])[:20]),
        })
        return context
