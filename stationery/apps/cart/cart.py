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
        if not offer_ids:
            return

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
        self.session[CART_SESSION_ID] = {}
        self.session.modified = True

    def add_offer(self, offer_id, quantity=1, update_quantity=False):
        """
        Добавление нового товара в корзину или изменение кол-ва.
        """
        offer_id = str(offer_id)

        if offer_id not in self.cart:
            self.cart[offer_id] = {'quantity': 0}

        if update_quantity:
            new_quantity = quantity
        else:
            new_quantity = self.cart[offer_id]['quantity'] + quantity

        # Если на складе не хватает товара, то мы не его добавляем в корзину.
        instance = Offer.objects.get(pk=offer_id)
        if new_quantity < 0 or new_quantity > instance.rest_limit:
            if self.cart[offer_id]['quantity'] == 0:
                del self.cart[offer_id]
            return -1

        self.cart[offer_id]['quantity'] = new_quantity

        if self.cart[offer_id]['quantity'] == 0:
            del self.cart[offer_id]

        self.save()

    def remove_offer(self, offer_id):
        """
        Удаление товара из корзины.
        """
        offer_id = str(offer_id)

        if offer_id in self.cart:
            del self.cart[offer_id]
            self.save()

    def get_total_price(self):
        """
        Получение полной цены.
        """
        return sum(Decimal(offer['instance'].retail_price) * offer['quantity']
                   for offer in self)

    def get_total_weight(self):
        """
        Получение веса всех товаров в корзине.
        """
        weight = 0
        for offer in self:
            weight += offer['instance'].weight * offer['quantity']
        return int(weight)
