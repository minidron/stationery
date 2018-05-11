from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from mptt.admin import DraggableMPTTAdmin

from sorl.thumbnail.admin import AdminImageMixin

from lib.utils import l

from odinass import models as odinass_models


@admin.register(odinass_models.Category)
class CategoryAdmin(DraggableMPTTAdmin):
    search_fields = [
        'title',
    ]

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
                'order',
            ),
        }),
    )


@admin.register(odinass_models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_selected',
    ]

    readonly_fields = [
        'id',
        'title',
    ]


@admin.register(odinass_models.Property)
class PropertyAdmin(admin.ModelAdmin):
    search_fields = [
        'title',
    ]

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


@admin.register(odinass_models.PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    pass


@admin.register(odinass_models.Product)
class ProductAdmin(AdminImageMixin, admin.ModelAdmin):
    list_per_page = 10

    list_display = [
        'title',
        'article',
        'created',
    ]

    search_fields = [
        'title',
        'article',
    ]

    list_filter = [
        'created',
        'is_favorite',
    ]

    readonly_fields = [
        'article',
        'category',
        'field_offers',
        'field_properties',
        'id',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'category',
                'image',
                'is_favorite',
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
        values = instance.offers.all()
        if not values:
            return ''
        return mark_safe('<br />'.join(
            ['&middot; %s' % l(reverse('admin:odinass_offer_change',
                                       args=[v.pk]), v) for v in values]))
    field_offers.short_description = 'предложения'

    def field_properties(self, instance):
        values = instance.property_values.all()
        if not values:
            return ''
        values_list = []
        for value in values:
            p_link = l(reverse('admin:odinass_property_change',
                               args=[value.property.pk]), value.property)
            v_link = l(reverse('admin:odinass_propertyvalue_change',
                               args=[value.pk]), value)
            link = '%s - %s' % (p_link, v_link)
            values_list.append(link)
        return mark_safe('<br />'.join(values_list))
    field_properties.short_description = 'свойства'


@admin.register(odinass_models.ProductOrder)
class ProductOrderAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Админка для `Новинки`.
    """
    list_per_page = 100
    list_filter = []
    list_display_links = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_favorite=True)


@admin.register(odinass_models.PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_default',
    ]


@admin.register(odinass_models.Offer)
class OfferAdmin(admin.ModelAdmin):
    search_fields = [
        'title',
    ]

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


@admin.register(odinass_models.Log)
class LogAdmin(admin.ModelAdmin):
    """
    Админка для логирования 1С
    """
    list_display = [
        'created',
        'filename',
        'action',
        'status',
    ]
