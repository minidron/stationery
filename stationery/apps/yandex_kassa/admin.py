from django.contrib import admin

from yandex_kassa.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Админ панель для `Платежа`.
    """
