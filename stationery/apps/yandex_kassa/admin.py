from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import redirect

from yandex_kassa.interface import YandexKassaInterface
from yandex_kassa.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Админ панель для `Платежа`.
    """
    list_display = [
        'payment_id',
        'payment_method',
        'order_id',
        'amount',
        'status',
        'created_at',
        'captured_at',
        'expires_at',
        'payer',
    ]

    list_filter = [
        'status',
        'created_at',
        'captured_at',
        'expires_at',
    ]

    search_fields = [
        'payment_id',
        'order_id',
        'payer_phone',
        'payer_email',
    ]

    def has_add_permission(self, request):
        """
        Убираем возможность ручного добавления.
        """
        return False

    def get_readonly_fields(self, request, obj=None):
        """
        Все поля в readonly.
        """
        return self.fields or [f.name for f in self.model._meta.fields]

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            url(r'^(?P<pk>\d+)/update/$',
                self.admin_site.admin_view(self.update_view),
                name='%s_%s_update' % info),
        ]
        urls.extend(super().get_urls())
        return urls

    def update_view(self, request, pk=None, **kwargs):
        """
        Обновляем информацию о платеже.
        """
        payment = self.get_object(request, pk)

        interface = YandexKassaInterface()
        payment_data = interface.payment_status(payment.payment_id)

        for attr, value in payment_data.items():
            if value is not None:
                setattr(payment, attr, value)
        payment.save()

        info = self.model._meta.app_label, self.model._meta.model_name
        return redirect('admin:%s_%s_changelist' % info)
