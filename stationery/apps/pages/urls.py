from django.conf.urls import url

from pages import views as views_pages


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views_pages.PageView.as_view(), name='static'),
]
