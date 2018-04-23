from django.conf.urls import url

from pages import views as views_pages


urlpatterns = [
    url(r'^поиск/$',
        views_pages.SearchOfferView.as_view(), name='search'),
    url(r'^контакты/$',
        views_pages.OfficeListView.as_view(), name='contact'),
    url(r'^мастер-классы/$',
        views_pages.BlogListView.as_view(), name='blog'),
    url(r'^мастер-классы/(?P<pk>[0-9a-f-]+)/$',
        views_pages.BlogDetailView.as_view(), name='blog_detail'),
    url(r'^каталог/(?P<pk>[0-9a-f-]+)/$',
        views_pages.CategoryView.as_view(), name='category'),
    url(r'^товар/(?P<pk>[0-9a-f-]+)/$',
        views_pages.ProductView.as_view(), name='product'),
    url(r'^(?P<slug>[-\w]+)/$',
        views_pages.PageView.as_view(), name='static'),
]
