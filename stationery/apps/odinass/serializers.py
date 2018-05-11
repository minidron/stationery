import operator
import re

from functools import reduce

from django.db.models import Q, Value
from django.db.models.functions import Concat

import django_filters

from rest_framework import serializers

from odinass.models import Offer


def escape(s):
    return re.sub(r'[(){}\[\].*?|^$\\+-]', r'\\\g<0>', s)


class OfferTitleFilter(django_filters.Filter):
    """
    Поиск для автокомплита.
    """
    max_result = 10

    def filter(self, qs, value):
        qs = qs.annotate(full_name=Concat('product__article', Value(' '),
                                          'title'))
        bits = value.split(' ')
        if len(bits) is 1 and bits[0].isdecimal():
            full_name_clauses = Q(full_name__icontains=bits[0])
        else:
            full_name_clauses = reduce(
                operator.and_,
                [Q(full_name__iregex=r'(^|\s)%s' % escape(v)) for v in bits])
        return qs.filter(full_name_clauses)[:self.max_result]


class OfferQFilter(OfferTitleFilter):
    """
    Поиск для страницы поиска.
    """
    max_result = 200


class SearchOfferFilter(django_filters.FilterSet):
    title = OfferTitleFilter()
    q = OfferQFilter()

    class Meta:
        fields = ('title', 'q')
        model = Offer


class SearchOfferSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    price_retail = serializers.CharField(source='price', read_only=True)

    class Meta:
        fields = '__all__'
        model = Offer
