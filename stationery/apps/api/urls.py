from rest_framework.routers import DefaultRouter

from orders.api import OrderViewSet


router = DefaultRouter()

router.register('orders', OrderViewSet)
