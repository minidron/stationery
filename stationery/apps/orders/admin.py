from django.contrib import admin

from orders import models as orders_models


@admin.register(orders_models.Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(orders_models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
