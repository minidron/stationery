from decimal import Decimal

from cart.conf import CART_SESSION_ID

from odinass.models import Offer


class Cart(object):
    """
    Корзина товаров.
    """
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        offer_ids = self.cart.keys()
        offers = Offer.objects.offers(user=self.request.user, ids=offer_ids)

        for offer in offers:
            yield {
                'instance': offer,
                'quantity': self.cart[str(offer.pk)]['quantity'],
            }

    def save(self):
        """
        Сохранение изменение в корзине (сохраняем сессию).
        """
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        """
        Очистка корзины.
        """
        del self.session[CART_SESSION_ID]

    def add_offer(self, offer_id, quantity=1, update_quantity=False):
        """
        Добавление нового товара в корзину или изменение кол-ва.
        """
        if offer_id not in self.cart:
            self.cart[offer_id] = {'quantity': 0}

        if update_quantity:
            self.cart[offer_id]['quantity'] = quantity
        else:
            self.cart[offer_id]['quantity'] += quantity

        if self.cart[offer_id]['quantity'] == 0:
            del self.cart[offer_id]

        self.save()

    def remove_offer(self, offer_id):
        """
        Удаление товара из корзины.
        """
        if offer_id in self.cart:
            del self.cart[offer_id]
            self.save()

    def get_total_price(self):
        """
        Получение полной цены.
        """
        return sum(Decimal(offer['instance'].retail_price) * offer['quantity']
                   for offer in self)
