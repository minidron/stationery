import uuid

from django.utils import dateparse

from yookassa import Payment

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

    def create_payment(self, data):
        """
        Создать платёж.
        """
        payment = Payment.create(data, self.generate_idempotence_key())

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
        payment = Payment.find_one(payment_id)

        created_at = (dateparse.parse_datetime(payment.created_at)
                      if payment.created_at else None)
        captured_at = (dateparse.parse_datetime(payment.captured_at)
                       if payment.captured_at else None)
        expires_at = (dateparse.parse_datetime(payment.expires_at)
                      if payment.expires_at else None)

        return {
            'amount': payment.amount.value,
            'captured_at': captured_at,
            'created_at': created_at,
            'currency': payment.amount.currency,
            'description': payment.description,
            'expires_at': expires_at,
            'metadata': payment.metadata,
            'payment_method': payment.payment_method.type,
            'receipt_registration': payment.receipt_registration,
            'status': payment.status,
        }
