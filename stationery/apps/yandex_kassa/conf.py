from collections import MutableMapping

from django.conf import settings as _settings
from django.core.signals import setting_changed
from django.dispatch import receiver

from yandex_checkout import Configuration


DEFAULTS = {
    'DEBUG': _settings.DEBUG,

    'SHOP_ID': '',
    'SECRET_KEY': '',

    'PAYMENT_DEFAULT_CURRENCY': 'RUB',
    'PAYMENT_CURRENCY': [
        'RUB',  # российский рубль
        'USD',  # доллар США
        'EUR',  # евро
        'BYN',  # белорусский рубль
        'CNY',  # китайский юань
        'KZT',  # казахстанский тенге
        'UAH',  # украинская гривна
    ],

    'PAYMENT_DEFAULT_METHOD': 'yandex_money',
    'PAYMENT_METHOD': [
        'yandex_money',  # Яндекс.Деньги
        'bank_card',  # банковская карта
        'sberbank',  # Сбербанк Онлайн (интернет-банк Сбербанка)
        'cash',  # оплата наличными в терминале
        'mobile_balance',  # баланс мобильного телефона
        'qiwi',  # QIWI Кошелек
        'webmoney',  # Webmoney
        # 'alfabank',  # Альфа-Клик (интернет-банк Альфа-Банка)
        'installments',  # оплата через сервис «Заплатить по частям»
    ],
}


class YandexKassaSettings(MutableMapping):
    """
    Контейнер для настроек Яндекс.Кассы.
    """

    def __init__(self, wrapped_settings):
        self.settings = DEFAULTS.copy()
        self.settings.update(wrapped_settings)

    def __getitem__(self, key):
        value = self.settings[key]
        if key in ['SHOP_ID', 'SECRET_KEY'] and not value:
            raise NotImplementedError(
                'Необходимо указать `%s` в настройках `YANDEX_KASSA`.' % key)
        return value

    def __setitem__(self, key, value):
        self.settings[key] = value

    def __delitem__(self, key):
        del self.settings[key]

    def __iter__(self):
        return iter(self.settings)

    def __len__(self):
        return len(self.settings)

    def __getattr__(self, name):
        return self.__getitem__(name)


settings = YandexKassaSettings(getattr(_settings, 'YANDEX_KASSA', {}))
Configuration.configure(settings.SHOP_ID, settings.SECRET_KEY)


@receiver(setting_changed)
def reload_settings(**kwargs):
    """
    Обновление настроек, если они изменились.
    """
    if kwargs['setting'] == 'YANDEX_KASSA':
        settings.update(kwargs['value'])
        Configuration.configure(settings.SHOP_ID, settings.SECRET_KEY)
