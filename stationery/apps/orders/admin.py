from django.contrib import admin

from orders.models import Item, Order


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
