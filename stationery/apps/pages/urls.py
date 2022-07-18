from django.conf.urls import url

from pages import views as views_pages

urlpatterns = [
    url(r'^search/$',
        views_pages.SearchOfferView.as_view(), name='search'),
    url(r'^contacts/$',
        views_pages.OfficeListView.as_view(), name='contacts'),
    url(r'^workshop/$',
        views_pages.BlogListView.as_view(), name='blog'),
    url(r'^workshop/(?P<pk>[0-9a-f-]+)/$',
        views_pages.BlogDetailView.as_view(), name='blog_detail'),
    url(r'^catalog/(?P<path>[-\w\/]+)/$',
        views_pages.catalog_view, name='catalog'),
     url(r'catalog',
         views_pages.TagsView.as_view(), name='tags'),
    url(r'^(?P<slug>[-\w]+)/$',
        views_pages.PageView.as_view(), name='static'),
]
