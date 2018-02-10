from functools import reduce
import operator

from django.db.models import Q
from django.db.models.functions import Concat

import django_filters

from rest_framework import serializers

from odinass.models import Offer


class OfferTitleFilter(django_filters.Filter):
    def filter(self, qs, value):
        qs = qs.annotate(full_name=Concat('title', 'product__article'))
        bits = value.split(' ')
        full_name_clauses = reduce(operator.and_,
                                   [Q(full_name__istartswith=v) for v in bits])
        return qs.filter(full_name_clauses)[:10]


class SearchOfferFilter(django_filters.FilterSet):
    title = OfferTitleFilter()

    class Meta:
        fields = ('title', )
        model = Offer


class SearchOfferSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    price_retail = serializers.CharField(source='price', read_only=True)

    class Meta:
        fields = '__all__'
        model = Offer
