from django.conf import settings

import requests

from rest_framework import authentication, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import (
    AddressSerializer, ItemSerializer, OrderSerializer)
from orders.utils import fetch_delivery_price


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели `Order`.
    """
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related('items')

    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    ]

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.GET:
            qs = qs.none()
        return qs

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def cart(self, request):
        """
        Получаем информацию о корзине пользователя.
        """
        order = Order.get_cart(request.user)
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """
        Добавляем товар в корзину.
        """
        offer_id = request.data.get('offer_id', None)
        quantity = int(request.data.get('quantity', 0))

        if not all([offer_id, quantity]):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        order = Order.get_cart(request.user)
        item = order.add_item(offer_id, quantity, user=request.user)
        if not item:
            return Response({'error': 'limit'}, status=status.HTTP_200_OK)

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_from_cart(self, request):
        """
        Удаляем товар из корзины.
        """
        offer_id = request.data.get('offer_id', None)

        if not offer_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        order = Order.get_cart(request.user)
        order.remove_item(offer_id)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def delivery_price(self, request):
        """
        Получаем цену доставки.
        """
        data = request.data
        order = Order.objects.get(pk=data.get('order_id'))
        price = fetch_delivery_price(
            data.get('delivery_type'),
            '142200',
            data.get('zip_code'),
            order.weight)
        return Response({'price': price}, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ViewSet):
    """
    ViewSet для подсказок адресов.
    """
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    ]

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @action(detail=False, methods=['get'])
    def suggest(self, request):
        """
        Подсказки адресов.
        """
        query = request.GET.get('query')

        url = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address'  # NOQA
        data = {'query': query}

        headers = {
            'Authorization': 'Token %s' % settings.DADATA_TOKEN,
        }

        req = requests.post(url, timeout=2, json=data, headers=headers)
        data = req.json()['suggestions']

        serializer = AddressSerializer(list(map(lambda x: {
            'address': x['value'],
            'zip_code': x['data'].get('postal_code', ''),
        }, data)), many=True)
        return Response(serializer.data)
