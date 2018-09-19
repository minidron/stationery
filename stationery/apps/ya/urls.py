from django.conf.urls import url
from django.views.generic import TemplateView

from yandex_money.views import CheckOrderFormView, NoticeFormView

from ya.views import OrderView


urlpatterns = [
    url(r'^order/$',
        OrderView.as_view(), name='yandex_money_order'),
    url(r'^check/$',
        CheckOrderFormView.as_view(), name='yandex_money_check'),
    url(r'^aviso/$',
        NoticeFormView.as_view(), name='yandex_money_notice'),
    url(r'^success/$',
        TemplateView.as_view(), name='yandex_money_success'),
    url(r'^fail/$',
        TemplateView.as_view(), name='yandex_money_fail'),
]
