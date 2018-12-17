from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from mptt.admin import DraggableMPTTAdmin

from sorl.thumbnail.admin import AdminImageMixin

from lib.utils import l

from odinass import models as odinass_models
from odinass.models import Category


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
                'content',
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

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False


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

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False


@admin.register(odinass_models.Property)
class PropertyAdmin(admin.ModelAdmin):
    search_fields = [
        'title',
    ]

    list_display = [
        'title',
        'is_weight',
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
                'is_weight',
            ),
        }),
        ('Дополнительно', {
            'fields': (
                'id',
                'value_type',
            ),
        }),
    )

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False

    def field_values(self, instance):
        values = instance.property_values.values_list('title', flat=True)
        if not values:
            return ''
        return mark_safe('<br />'.join(['&middot; %s' % v for v in values]))
    field_values.short_description = 'варианты значений'


@admin.register(odinass_models.PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False


class EmptyImageListFilter(admin.SimpleListFilter):
    field_name = 'image'
    parameter_name = 'image'
    title = 'есть изображение'

    def lookups(self, request, model_admin):
        return (
            (1, 'Да'),
            (0, 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value():
            params = (
                Q(**{'%s' % self.field_name: ''})
            )
            if self.value() == '0':
                return queryset.filter(params)
            if self.value() == '1':
                return queryset.exclude(params)
        return queryset


class PublishedListFilter(admin.SimpleListFilter):
    field_name = 'is_published'
    parameter_name = 'is_published'
    title = 'опубликовано на сайте'

    def lookups(self, request, model_admin):
        return (
            (1, 'Да'),
            (0, 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value():
            not_published_categories = (
                Category.objects
                        .get_queryset_descendants(
                            Category.objects.filter(is_published=False),
                            include_self=True))

            if self.value() == '0':
                return queryset.filter(category__in=not_published_categories)
            if self.value() == '1':
                return queryset.exclude(category__in=not_published_categories)
        return queryset


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
        EmptyImageListFilter,
        PublishedListFilter,
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
                'content',
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

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False

    def field_offers(self, instance):
        values = instance.offers.all()
        if not values:
            return ''
        return mark_safe('<br />'.join(
            ['&middot; %s' % l(reverse('admin:odinass_offer_change',
                                       args=[v.pk]), v) for v in values]))
    field_offers.short_description = 'предложения'

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            url(r'^(?P<pk>[0-9a-f-]+)/deleteproperty/(?P<property_pk>[0-9a-f-]+)/$',  # NOQA
                self.admin_site.admin_view(self.delete_property_view),
                name='%s_%s_deleteproperty' % info),
        ]
        urls.extend(super().get_urls())
        return urls

    def delete_property_view(self, request, **kwargs):
        product = odinass_models.Product.objects.get(pk=kwargs['pk'])
        property_value = odinass_models.PropertyValue.objects.get(
            pk=kwargs['property_pk'])
        product.property_values.remove(property_value)
        messages.success(request, 'Свойство было успешно удалено.')
        info = self.model._meta.app_label, self.model._meta.model_name
        return redirect('admin:%s_%s_change' % info, kwargs['pk'])

    def field_properties(self, instance):
        values = instance.property_values.all()
        if not values:
            return ''
        values_list = []
        for value in values:
            p_value = '%s - %s' % (value.property, value)
            delete = l(reverse('admin:odinass_product_deleteproperty',
                               args=[instance.pk, value.pk]), 'удалить')
            values_list.append('%s %s' % (p_value, delete))
        return mark_safe('<br />'.join(values_list))
    field_properties.short_description = 'свойства'


class ProductOrderChangeList(ChangeList):
    def url_for_result(self, result):
        return reverse('admin:odinass_product_change',
                       args=[result.product_id])


@admin.register(odinass_models.ProductOrder)
class ProductOrderAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Админка для `Новинки`.
    """
    list_per_page = 100

    list_display = [
        'product',
        'field_order',
    ]

    readonly_fields = [
        'field_order',
    ]

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False

    def field_order(self, instance):
        return mark_safe(instance.order)
    field_order.short_description = 'порядок'

    def get_changelist(self, request, **kwargs):
        super().get_changelist(request, **kwargs)
        return ProductOrderChangeList


@admin.register(odinass_models.PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_default',
    ]

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False


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

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False

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

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False


@admin.register(odinass_models.Rest)
class RestAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False


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

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False
