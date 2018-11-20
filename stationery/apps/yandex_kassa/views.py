import json
from json import JSONDecodeError

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from yandex_kassa.interface import YandexKassaInterface
from yandex_kassa.models import Payment


@csrf_exempt
def notification(request):
    # TODO: Проверка на входные данные.
    try:
        data = json.loads(request.body.decode())
    except JSONDecodeError:
        return HttpResponse(status=200)

    payment = get_object_or_404(Payment, payment_id=data['object']['id'])

    interface = YandexKassaInterface()
    payment_data = interface.payment_status(payment.payment_id)

    for attr, value in payment_data.items():
        if value is not None:
            setattr(payment, attr, value)
    payment.save()

    return HttpResponse(status=200)
