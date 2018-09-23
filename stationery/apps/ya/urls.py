from django.conf.urls import url

from yandex_money.views import CheckOrderFormView, NoticeFormView

from ya.views import SuccessPayment


urlpatterns = [
    url(r'^check/$',
        CheckOrderFormView.as_view(), name='yandex_money_check'),
    url(r'^aviso/$',
        NoticeFormView.as_view(), name='yandex_money_notice'),
    url(r'^success/$',
        SuccessPayment.as_view(), name='yandex_money_success'),
    url(r'^fail/$',
        SuccessPayment.as_view(), name='yandex_money_fail'),
]
