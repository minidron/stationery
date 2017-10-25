from django.contrib import admin
from django.utils.safestring import mark_safe

from mptt.admin import MPTTModelAdmin

from odinass.models import Category, Offer, Product, Property, PriceType, Price


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    readonly_fields = [
        'id',
        'title',
        'parent',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'is_published',
                'image',
            ),
        }),
        ('Дополнительно', {
            'fields': (
                'id',
                'parent',
            ),
        }),
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    readonly_fields = [
        'field_values',
        'id',
        'title',
        'value_type',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'field_values',
            ),
        }),
        ('Дополнительно', {
            'fields': (
                'id',
                'value_type',
            ),
        }),
    )

    def field_values(self, instance):
        values = instance.property_values.values_list('title', flat=True)
        if not values:
            return ''
        return mark_safe('<br />'.join(['&middot; %s' % v for v in values]))
    field_values.short_description = 'варианты значений'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories', )

    readonly_fields = [
        'article',
        'categories',
        'field_offers',
        'field_properties',
        'id',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'categories',
                'field_offers',
                'field_properties',
            ),
        }),
        ('Дополнительно', {
            'fields': (
                'id',
                'article',
            ),
        }),
    )

    def field_offers(self, instance):
        values = instance.offers.values_list('title', flat=True)
        if not values:
            return ''
        return mark_safe('<br />'.join(['&middot; %s' % v for v in values]))
    field_offers.short_description = 'предложения'

    def field_properties(self, instance):
        values = instance.property_values.values('title', 'property__title')
        if not values:
            return ''
        return mark_safe('<br />'.join(
            ['&middot; %s - %s' % (v['property__title'], v['title'])
             for v in values]))
    field_properties.short_description = 'свойства'


@admin.register(PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'sales_type',
    ]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    readonly_fields = [
        'product',
        'field_prices',
    ]

    def field_prices(self, instance):
        values = instance.prices.all()
        if not values:
            return ''
        return mark_safe('<br />'.join(['&middot; %s' % v for v in values]))
    field_prices.short_description = 'цены'


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    pass
