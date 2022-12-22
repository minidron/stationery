from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from hijack_admin.admin import HijackUserAdminMixin

from .models import User


@admin.register(User)
class AccountAdmin(UserAdmin, HijackUserAdminMixin):
    """
    Админка для управления пользователями.
    """
    ordering = ['email']
    search_fields = ['email']

    list_display = [
        'email',
        'first_name',
        'last_name',
        'company',
        'is_wholesaler',
        'hijack_field',
    ]

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'phone',
                'password',
            )
        }),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'price_type',
                'company',
                'is_wholesaler',
                'company_address',
                'inn',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
    )
