from django.conf.urls import url

from odinass.views import ExchangeView


urlpatterns = [
    url(r'^exchange$', ExchangeView.as_view(), name='exchange'),
]
