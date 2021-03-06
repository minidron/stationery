from rest_framework.routers import DefaultRouter

from cart.api import CartViewSet

from orders.api import AddressViewSet


router = DefaultRouter()

router.register(r'addresses', AddressViewSet, base_name='addresses')
router.register(r'cart', CartViewSet, base_name='cart')
