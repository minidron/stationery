import operator
import re
from functools import reduce

import django_filters
from django.conf import settings
from django.db.models import Case, When
from django.db.models import Q
from django_elasticsearch_dsl.search import Search
from elasticsearch.client import Elasticsearch
from odinass.models import Category, Offer
from rest_framework import serializers


def escape(s):
    return re.sub(r'[(){}\[\].*?|^$\\+-]', r'\\\g<0>', s)


class OfferTitleFilter(django_filters.Filter):
    """
    Поиск для автокомплита.
    """
    max_result = 5
    uniq_category = True

    def __init__(self, *args, **kwargs):
        self.hits_list = ()
        self.hits_order = ()
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        # инициализируем подключение
        client = Elasticsearch([settings.ELASTICSEARCH_HOST])
        value = value.lower()

        # формируем запрос
        search_query = {
            "bool": {
                "must_not": [  # исключает из выдачи is_published=False
                    {
                        "term": {
                            "is_published": False
                        }
                    }
                ],
                "should": [
                    {
                        "simple_query_string": {  # ищем что-то разумное
                            "fields": ["fullname", "category_name"],
                            "quote_field_suffix": ".exact",
                            "query": value
                        }
                    },
                    {
                        # частичное вхождение по строкам с транслитом (англ->рус)
                        # constant_score запрещает буст по частоте вхождения
                        "constant_score": {
                            "filter": {
                                "match": {
                                    "fullname_translit": {
                                        "query": value,
                                        "fuzziness": 1,
                                        "operator": "and",
                                    }
                                }
                            }
                        }
                    },
                ]
            }
        }

        # Инициализация запроса
        s = Search(using=client, index='offer') \
            .query(search_query)\
            .sort("_score", "-views")\
            .extra(size=self.max_result, from_=0)

        self.hits_list = []
        items = s.execute()
        if items:
            for item in items:
                self.hits_list.append(item.meta.id)
            # нужно для того, чтобы у выборки из пусгреса сохранился порядок, который вернул эластик
            self.hits_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(self.hits_list)])
            qs = qs.filter(id__in=self.hits_list).order_by(self.hits_order)
        else:
            qs = qs.none()

        # TODO: старая реализация. Может, оставить, как fallback?
        # else:
        #     qs = qs.annotate(full_name=Concat(
        #         'product__article', Value(' '),
        #         'product__title', Value(' '),
        #         'product__search_title'))
        #     bits = value.split(' ')
        #     if len(bits) is 1 and bits[0].isdecimal():
        #         full_name_clauses = Q(full_name__icontains=bits[0])
        #     else:
        #         full_name_clauses = reduce(
        #             operator.and_,
        #             [Q(full_name__iregex=r'(^|\s)%s' % escape(v))
        #              for v in bits])
        #
        #     unpublished = Category.objects.get_queryset_descendants(
        #         Category.objects.filter(is_published=False),
        #         include_self=True)
        #
        #     qs = (qs.filter(full_name_clauses)
        #             .exclude(product__category__in=unpublished))
        #
        #     if self.uniq_category:
        #         products = (qs.order_by('product__category__title')
        #                       .distinct('product__category__title'))
        #         qs = (qs.filter(id__in=products)
        #                 .order_by('-product__category__views'))

        return qs


class CategoryTitleFilter(django_filters.Filter):
    """
    Фильтр категорий по названию.
    """
    max_result = 5

    def filter(self, qs, value):
        client = Elasticsearch([settings.ELASTICSEARCH_HOST])
        value = value.lower()

        search_query = {
            "bool": {
                "must_not": [  # исключает из выдачи is_published=False
                    {
                        "term": {
                            "is_published": False
                        }
                    }
                ],
                "should": [
                    {
                        "simple_query_string": {
                            "fields": ["category_name"],
                            "quote_field_suffix": ".exact",
                            "query": value
                        }
                    },
                ]
            }
        }

        s = Search(using=client, index='category') \
            .query(search_query)\
            .sort("_score", "-views")\
            .extra(size=self.max_result, from_=0)

        hits_list = []
        items = s.execute()
        if items:
            for item in items:
                hits_list.append(item.meta.id)
            hits_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(hits_list)])
            qs = qs.filter(id__in=hits_list).order_by(hits_order)
        else:
            qs = qs.none()

            # TODO: fallback?
            # bits = value.split(' ')
            # search_clauses = reduce(operator.and_,
            #                         [Q(title__icontains=v) for v in bits])
            # unpublished = Category.objects.get_queryset_descendants(
            #     Category.objects.filter(is_published=False), include_self=True)
            # qs = (qs
            #       .exclude(pk__in=unpublished)
            #       .filter(search_clauses)
            #       .order_by('-views'))
        return qs[:self.max_result]


class OfferQFilter(OfferTitleFilter):
    """
    Поиск для страницы поиска.
    """
    max_result = 200
    uniq_category = False


class SearchOfferFilter(django_filters.FilterSet):
    title = OfferTitleFilter()
    q = OfferQFilter()

    class Meta:
        fields = ('title', 'q')
        model = Offer


class SearchCategoryFilter(django_filters.FilterSet):
    """
    Фильтры для поиска категорий.
    """
    title = CategoryTitleFilter()

    class Meta:
        fields = ('title',)
        model = Category


class SearchOfferSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    category = serializers.CharField(source='product.category', read_only=True)
    # price_retail = serializers.CharField(source='price', read_only=True)
    price_retail = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(source='full_title', read_only=True)

    class Meta:
        fields = '__all__'
        model = Offer

    def get_price_retail(self, obj):
        request = self.context.get('request')
        user = None
        if request and hasattr(request, 'user'):
            user = request.user
        return obj.price(user=user)


class SearchCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для результата поиска категории.
    """
    url = serializers.CharField(
        source='get_absolute_url', read_only=True)

    class Meta:
        fields = ['id', 'url', 'title']
        model = Category
