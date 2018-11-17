from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import FloatField, F, Sum
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin

from orders.models import (GroupSettings, Item, Office, Order, OrderStatus,
                           Profile)


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
                'field_items',
            ),
        }),
    )

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


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Админка для товаров заказа.
    """
    raw_id_fields = ['offer']

    list_display = [
        'offer',
        'quantity',
    ]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Админка для профиля пользователя.
    """


@admin.register(GroupSettings)
class GroupSettingsAdmin(admin.ModelAdmin):
    """
    Админка для настроек групп.
    """


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


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    list_display = [
        'username',
        'email',
        'field_company',
        'first_name',
        'last_name',
        'field_inn',
        'field_price_type',
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


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
