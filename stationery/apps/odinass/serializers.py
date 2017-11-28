# from functools import reduce
# import operator

# from django.db.models import Q, Case, When, IntegerField

import django_filters

from rest_framework import serializers

from odinass.models import Offer


class OfferTitleFilter(django_filters.Filter):
    def filter(self, qs, value):
        # qs = qs.annotate(full_name=Offer('title', 'region__short_title'))
        # bits = value.split(' ')
        # offer_title = reduce(operator.and_,
        #                      [Q(title__icontains=v) for v in bits])
        # qs = qs.annotate(title_matches=Case(
        #     When(offer_title, then=1), default=0, output_field=IntegerField()))  # NOQA
        return qs.filter(title__icontains=value)


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
