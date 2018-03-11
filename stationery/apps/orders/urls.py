from django.conf.urls import url

from orders import views as orders_views


urlpatterns = [
    url(r'^cart/$', orders_views.CartView.as_view(), name='cart'),
    url(r'^registration/$', orders_views.RegistrationView.as_view(),
        name='registration'),
    url(r'^login/$', orders_views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', orders_views.UserLogoutView.as_view(), name='logout'),
    url(r'^history/$', orders_views.HistoryListView.as_view(), name='history'),
    url(r'^history/(?P<pk>\d+)/$', orders_views.HistoryDetailView.as_view(),
        name='history_detail'),
]
