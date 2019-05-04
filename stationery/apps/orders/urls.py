from django.conf.urls import url

from cart import views as cart_views

from orders import views as orders_views


urlpatterns = [
    url(r'^$',
        orders_views.UserProfileView.as_view(), name='index'),
    url(r'^cart/$',
        cart_views.CartView.as_view(), name='cart'),
    url(r'^registration/$',
        orders_views.RegistrationView.as_view(), name='registration'),
    url(r'^profile/$',
        orders_views.UpdateProfileView.as_view(), name='profile'),
    url(r'^login/$',
        orders_views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$',
        orders_views.UserLogoutView.as_view(), name='logout'),
    url(r'^history/$',
        orders_views.HistoryListView.as_view(), name='history'),
    url(r'^history/(?P<pk>\d+)/$',
        orders_views.HistoryDetailView.as_view(), name='history_detail'),
]
