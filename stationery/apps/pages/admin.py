from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from pages.models import Page


@admin.register(Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {
        'slug': (
            'title',
        )
    }

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'slug',
                'icon',
                'content',
            ),
        }),
    )
