from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from yandex_kassa.conf import settings as kassa_settings


class PaymentStatus:
    """
    Статусы платежа.
    """
    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'

    CHOICES = (
        (PENDING, 'Создан'),
        (WAITING_FOR_CAPTURE, 'Ожидает подтверждения'),
        (SUCCEEDED, 'Завершен'),
        (CANCELED, 'Отменен'),
    )


class PaymentCurrency:
    """
    Валюта платежа.
    """
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'
    BYN = 'BYN'
    CNY = 'CNY'
    KZT = 'KZT'
    UAH = 'UAH'

    CHOICES = (
        (RUB, 'Российский рубль'),
        (USD, 'Доллар США'),
        (EUR, 'Евро'),
        (BYN, 'Белорусский рубль'),
        (CNY, 'Китайский юань'),
        (KZT, 'Казахстанский тенге'),
        (UAH, 'Украинская гривна'),
    )


class PaymentMethod:
    """
    Способы оплаты.
    """
    ALFABANK = 'alfabank'
    APPLEPAY = 'apple_pay'
    B2B_SBERBANK = 'b2b_sberbank'
    BANK_CARD = 'bank_card'
    CASH = 'cash'
    GOOGLE_PAY = 'google_pay'
    INSTALMENTS = 'installments'
    MOBILE_BALANCE = 'mobile_balance'
    PSB = 'psb'
    QIWI = 'qiwi'
    SBERBANK = 'sberbank'
    WEBMONEY = 'webmoney'
    YANDEX_MONEY = 'yandex_money'

    CHOICES = (
        (ALFABANK, 'Альфа-Клик'),
        (APPLEPAY, 'Apple Pay'),
        (B2B_SBERBANK, 'Сбербанк Бизнес Онлайн'),
        (BANK_CARD, 'Банковская карта'),
        (CASH, 'Наличные'),
        (GOOGLE_PAY, 'Google Pay'),
        (INSTALMENTS, 'Заплатить по частям'),
        (MOBILE_BALANCE, 'Баланс мобильного телефона'),
        (PSB, 'Интернет-банк Промсвязьбанка'),
        (QIWI, 'QIWI Кошелек'),
        (SBERBANK, 'Сбербанк Онлайн'),
        (WEBMONEY, 'Webmoney'),
        (YANDEX_MONEY, 'Яндекс.Деньги'),
    )


class ReceiptRegistrationStatus:
    """
    Статусы доставки чека в онлайн-кассу.
    """
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'

    CHOICES = (
        (PENDING, 'Создан'),
        (SUCCEEDED, 'Завершен'),
        (CANCELED, 'Отменен'),
    )


class Payment(models.Model):
    """
    Модель `Платёж` через Яндекс.Кассы.
    """

    # Данные платежа.
    payment_id = models.CharField(
        'идентификатор',
        max_length=36)
    status = models.CharField(
        'статус',
        max_length=20, choices=PaymentStatus.CHOICES,
        default=PaymentStatus.PENDING, db_index=True)
    amount = models.DecimalField(
        'сумма',
        max_digits=15, decimal_places=2)
    currency = models.CharField(
        'валюта',
        max_length=3, choices=PaymentCurrency.CHOICES,
        default=kassa_settings.PAYMENT_DEFAULT_CURRENCY)
    payment_method = models.CharField(
        'способ оплаты',
        max_length=20, choices=PaymentMethod.CHOICES,
        default=kassa_settings.PAYMENT_DEFAULT_METHOD)
    description = models.TextField(
        'описание транзакции',
        blank=True)
    metadata = JSONField(
        'дополнительные данные',
        blank=True, null=True, default=dict)

    # Данные для формирования чека в онлайн-кассе.
    receipt_registration = models.CharField(
        'статус доставки чека в онлайн-кассу',
        max_length=20, blank=True, choices=ReceiptRegistrationStatus.CHOICES,
        db_index=True)

    # Время и даты.
    created_at = models.DateTimeField(
        'время создания',
        editable=False, default=timezone.now)
    captured_at = models.DateTimeField(
        'время подтверждения',
        editable=False, blank=True, null=True)
    expires_at = models.DateTimeField(
        'время отмены удержания',
        editable=False, blank=True, null=True)

    # Данные по заказу.
    order_id = models.TextField(
        'ID заказа',
        help_text='Внутренний номер заказа/товара.',
        max_length=100, blank=True)

    # Данные плательщика.
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='плательщик',
        on_delete=models.SET_NULL, blank=True, null=True)
    payer_email = models.EmailField(
        'email плательщика',
        max_length=100, blank=True)
    payer_phone = models.CharField(
        'телефон плательщика',
        max_length=20, blank=True)

    class Meta:
        default_related_name = '%(app_label)s_%(model_name)ss'
        get_latest_by = 'pk'
        ordering = ['-pk']
        verbose_name = 'платёж'
        verbose_name_plural = 'платежи'

    @property
    def is_paid(self):
        """
        Оплачен платёж или нет.
        """
        return self.status == PaymentStatus.SUCCEEDED
