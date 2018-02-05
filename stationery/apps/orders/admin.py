from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from orders.models import Item, Order, Profile


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админка для заказов.
    """


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


class ProfileInline(admin.StackedInline):
    can_delete = False
    fk_name = 'user'
    model = Profile
    verbose_name_plural = 'Настройки'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
