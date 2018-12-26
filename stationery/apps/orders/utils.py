import requests

from orders.models import DeliveryType


def safe_http_get(url, timeout=2, **kwargs):
    try:
        return requests.get(url, timeout=timeout, **kwargs)
    except requests.exceptions.RequestException:
        response = requests.Response()
        response.status_code = 404
        response._content = '{}'
        return response


def fetch_delivery_price(delivery_type, zip_code_from, zip_code_to, weight):
    delivery_type = int(delivery_type)

    # Самовывоз.
    if delivery_type == DeliveryType.EXW:
        return 0

    # Почта России.
    elif delivery_type == DeliveryType.RUSSIANPOST:
        url = 'https://tariff.russianpost.ru/tariff/v1/calculate'

        params = {
            'json': '',
            'object': 4030,
            'from': zip_code_from,
            'to': zip_code_to,
            'weight': weight,
        }

        response = safe_http_get(url, params=params)
        response_data = response.json()
        if response.status_code == 200 and 'errors' not in response_data:
            return response_data['paynds'] / 100
        else:
            return None
