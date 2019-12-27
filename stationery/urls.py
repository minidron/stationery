from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView, TemplateView

from filebrowser.sites import site

from rest_framework import routers

from yandex_kassa.views import notification

from api.urls import router as api_router

from pages.views import IndexView

from odinass.views import SearchCategoryViewSet, SearchOfferViewSet


router = routers.DefaultRouter()
router.register(r'search_category', SearchCategoryViewSet)
router.register(r'search_offer', SearchOfferViewSet)


urlpatterns = [
    url(r'^$',
        IndexView.as_view(), name='index'),
    url(r'^account/',
        include('orders.urls', namespace='account')),
    url(r'^api/v2/',
        include(api_router.urls, namespace='api-v2')),
    url(r'^api/',
        include(router.urls, namespace='api')),
    url(r'^yandex-notification/$',
        notification),
    url(r'^robots.txt$',
        TemplateView.as_view(
            template_name='robots.txt', content_type='text/plain')),
    url(r'^favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'), permanent=True)),
    url(r'^admin/filebrowser/',
        include(site.urls)),
    url(r'^admin/',
        include(admin.site.urls)),
    url(r'^1c/',
        include('odinass.urls', namespace='1c')),
    url(r'^hijack/',
        include('hijack.urls', namespace='hijack')),
    url(r'^',
        include('pages.urls', namespace='pages')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
