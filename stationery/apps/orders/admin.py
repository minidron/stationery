from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.db.models import F, FloatField, Sum
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin
from hijack_admin.admin import HijackUserAdminMixin

from orders.models import (
    GroupSettings, Item, Office, Order, OrderStatus, Profile)

UserModel = get_user_model()


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


class ProfileInline(admin.StackedInline):
    can_delete = False
    fk_name = 'user'
    model = Profile
    verbose_name_plural = 'Настройки'


class GroupSettingsInline(admin.StackedInline):
    can_delete = False
    fk_name = 'group'
    model = GroupSettings
    verbose_name_plural = 'Настройки'


class CustomUserAdmin(UserAdmin, HijackUserAdminMixin):
    inlines = (ProfileInline, )

    list_display = [
        'username',
        'email',
        'field_company',
        'first_name',
        'last_name',
        'field_inn',
        'field_price_type',
        'hijack_field',
    ]

    def field_company(self, instance):
        company = instance.profile.company
        return mark_safe(company if company else '')
    field_company.short_description = 'Компания'

    def field_inn(self, instance):
        inn = instance.profile.inn
        return mark_safe(inn if inn else '')
    field_inn.short_description = 'ИНН'

    def field_price_type(self, instance):
        price_type = instance.profile.price_type
        return mark_safe(price_type if price_type else '')
    field_price_type.short_description = 'Тип цены'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


class CustomGroupAdmin(GroupAdmin):
    inlines = (GroupSettingsInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


class OfficeFormAdmin(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'coordinates': forms.TextInput(),
        }


@admin.register(Office)
class OfficeAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = OfficeFormAdmin


admin.site.register(UserModel, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
