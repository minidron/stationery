from django.conf import settings

import requests

from rest_framework import authentication, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.serializers import AddressSerializer


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
