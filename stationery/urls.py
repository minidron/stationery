from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView, TemplateView

from rest_framework import routers

from pages.views import IndexView

from odinass.views import SearchOfferViewSet

from orders.views import CartView, OrderAPIView, UserLoginView, UserLogoutView


router = routers.DefaultRouter()
router.register(r'search_offer', SearchOfferViewSet)


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^login/$', UserLoginView.as_view(), name='login'),
    url(r'^logout/$', UserLogoutView.as_view(), name='logout'),
    url(r'^api/orders/$', OrderAPIView.as_view()),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^robots.txt$',
        TemplateView.as_view(
            template_name='robots.txt', content_type='text/plain')),
    url(r'^favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'), permanent=True)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^1c/', include('odinass.urls', namespace='1c')),
    url(r'^', include('pages.urls', namespace='pages')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
