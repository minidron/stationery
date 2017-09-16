from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from odinass.models import Category, Product, Property, PropertyValue


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    readonly_fields = [
        'id',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'id',
                'title',
                'parent',
            ),
        }),
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    pass


@admin.register(PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories', 'property_values')
