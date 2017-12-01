from django.contrib import admin
from django.utils.safestring import mark_safe

from mptt.admin import MPTTModelAdmin

from odinass import models as odinass_models


@admin.register(odinass_models.Category)
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


@admin.register(odinass_models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    readonly_fields = [
        'id',
        'title',
    ]


@admin.register(odinass_models.Property)
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


@admin.register(odinass_models.Product)
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


@admin.register(odinass_models.PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'sales_type',
    ]


@admin.register(odinass_models.Offer)
class OfferAdmin(admin.ModelAdmin):
    readonly_fields = [
        'product',
        'field_prices',
        'field_rests',
    ]

    def field_prices(self, instance):
        values = instance.prices.all()
        if not values:
            return ''
        return mark_safe('<br />'.join(['&middot; %s' % v for v in values]))
    field_prices.short_description = 'цены'

    def field_rests(self, instance):
        values = instance.rests.all()
        if not values:
            return ''
        return mark_safe('<br />'.join([
            '&middot; %s - %s' % (v.warehouse, v.value) for v in values]))
    field_rests.short_description = 'остатки'


@admin.register(odinass_models.Price)
class PriceAdmin(admin.ModelAdmin):
    pass


@admin.register(odinass_models.Rest)
class RestAdmin(admin.ModelAdmin):
    pass
