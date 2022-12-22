from django import forms
from django.contrib import admin
from django.db.models import F, FloatField, Sum
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from orders.models import Item, Office, Order, OrderStatus


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0

    readonly_fields = [
        'offer',
    ]

    fields = [
        'offer',
        'quantity',
        'unit_price',
    ]

    def has_add_permission(self, request):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админка для заказов.
    """
    inlines = [ItemInline]

    readonly_fields = [
        'field_items',
    ]

    search_fields = [
        'id',
    ]

    list_display = [
        'id',
        'user',
        'status',
        'created',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'status',
                'gain',
                'comment',
                'delivery_type',
                'delivery_price',
                'zip_code',
                'delivery_address',
                'field_items',
            ),
        }),
    )

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (qs.prefetch_related('items__offer__product')
                  .exclude(status=OrderStatus.NOT_CREATED))

    def field_items(self, instance):
        qs = instance.items.all()
        return mark_safe(render_to_string('orders/admin/items.html', {
            'items': qs,
            'total_quantity': (
                qs.aggregate(Sum('quantity')).get('quantity__sum', 0)),
            'total_price': (
                qs.aggregate(total=Sum(F('unit_price') * F('quantity'),
                                       output_field=FloatField()))
                  .get('total', 0)),
        }))
    field_items.short_description = 'товары'


class OfficeFormAdmin(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'coordinates': forms.TextInput(),
        }


@admin.register(Office)
class OfficeAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = OfficeFormAdmin
