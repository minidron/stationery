import uuid

from django.utils import dateparse

from yandex_checkout import Payment

from yandex_kassa.exceptions import YandexKassaException
from yandex_kassa.models import PaymentMethod, PaymentStatus


class YandexKassaInterface:
    """
    Интерфейс для работы с Яндекс.Кассой.
    """

    def generate_idempotence_key(self):
        """
        Генерируем ключ идемпотентности.
        """
        return str(uuid.uuid4())

    def create_payment(self, payment_data):
        """
        Создать платёж.
        """
        payment = Payment.create(payment_data, self.generate_idempotence_key())

        # TODO: Сделать специальный класс для данной ошибки и описание.
        payment_status = payment.status
        if payment_status not in PaymentStatus.available_choices():
            raise YandexKassaException()

        # TODO: Сделать специальный класс для данной ошибки и описание.
        payment_payment_method = payment.payment_method.type
        if payment_payment_method not in PaymentMethod.available_choices():
            raise YandexKassaException()

        data = {
            'amount': payment.amount.value,
            'confirmation_url': payment.confirmation.confirmation_url,
            'created_at': dateparse.parse_datetime(payment.created_at),
            'currency': payment.amount.currency,
            'metadata': payment.metadata,
            'payment_id': payment.id,
            'payment_method': payment_payment_method,
            'status': payment_status,
        }

        if payment.description:
            data['description'] = payment.description

        return data

    def payment_status(self, payment_id):
        """
        Получить информацию о платеже.
        """
        return Payment.find_one(payment_id)
