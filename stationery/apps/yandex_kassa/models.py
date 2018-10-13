from django.conf import settings
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
    YANDEX_MONEY = 'yandex_money'
    BANK_CARD = 'bank_card'
    SBERBANK = 'sberbank'
    CASH = 'cash'
    MOBILE_BALANCE = 'mobile_balance'
    PSB = 'psb'
    QIWI = 'qiwi'
    WEBMONEY = 'webmoney'
    ALFABANK = 'alfabank'
    APPLEPAY = 'apple_pay'
    GOOGLE_PAY = 'google_pay'
    INSTALMENTS = 'installments'

    CHOICES = (
        (YANDEX_MONEY, 'Яндекс.Деньги'),
        (BANK_CARD, 'Банковская карта'),
        (SBERBANK, 'Сбербанк Онлайн'),
        (CASH, 'Наличными в терминале'),
        (MOBILE_BALANCE, 'Баланс мобильного телефона'),
        (PSB, 'Интернет-банк Промсвязьбанка'),
        (QIWI, 'QIWI Кошелек'),
        (WEBMONEY, 'Webmoney'),
        (ALFABANK, 'Альфа-Клик'),
        (APPLEPAY, 'Apple Pay'),
        (GOOGLE_PAY, 'Google Pay'),
        (INSTALMENTS, 'Через сервис "Заплатить по частям"'),
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
        default=PaymentStatus.PENDING)
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

    # Данные плательщика.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='пользователь',
        on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        default_related_name = '%(app_label)s_%(model_name)ss'
        verbose_name = 'платёж'
        verbose_name_plural = 'платежи'
