from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from yandex_kassa.models import Payment
from yandex_kassa.signals import payment_done

from lib.email import create_email

from orders.fields import YandexPointField


Group = 'auth.Group'
User = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class OrderStatus(object):
    """
    Статусы заказа.
    """
    NOT_CREATED = 1
    INWORK = 2
    CONFIRMED = 3
    DELIVERY = 4
    COMPLETED = 5
    CANCELED = 6

    CHOICES = (
        (NOT_CREATED, 'не создан'),
        (INWORK, 'в работе'),
        (CONFIRMED, 'подтвержденный'),
        (DELIVERY, 'доставка'),
        (COMPLETED, 'завершенный'),
        (CANCELED, 'аннулированный'),
    )

    CHOICES_MACHINE_NAME = {
        NOT_CREATED: 'not_created',
        INWORK: 'inwork',
        CONFIRMED: 'confirmed',
        DELIVERY: 'delivery',
        COMPLETED: 'completed',
        CANCELED: 'canceled',
    }


class DeliveryType(object):
    """
    Тип доставки.
    """
    EXW = 1
    RUSSIANPOST = 2

    CHOICES = (
        (EXW, 'Самовывоз'),
        (RUSSIANPOST, 'Почта России'),
    )

    CHOICES_MACHINE_NAME = {
        EXW: 'exw',
        RUSSIANPOST: 'russianpost',
    }


class OrderQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)


class Order(models.Model):
    """
    Заказ пользователя.
    """
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE)
    status = models.IntegerField(
        'статус',
        choices=OrderStatus.CHOICES, default=OrderStatus.NOT_CREATED,
        db_index=True)
    created = models.DateTimeField(
        'дата создания',
        editable=False, auto_now_add=True)
    updated = models.DateTimeField(
        'Дата изменения',
        editable=False, auto_now=True)
    gain = models.DecimalField(
        'приход',
        default=0,
        max_digits=12, decimal_places=2)
    comment = models.TextField(
        'комментарий к заказу',
        blank=True)
    delivery_type = models.IntegerField(
        'тип доставки',
        choices=DeliveryType.CHOICES, default=DeliveryType.EXW)
    delivery_price = models.DecimalField(
        'цена доставки',
        default=0,
        max_digits=12, decimal_places=2)
    delivery_address = models.TextField(
        'адрес доставки',
        blank=True)
    zip_code = models.CharField(
        'почтовый индекс',
        max_length=10, blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        default_related_name = 'orders'
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        if self.pk and self.status != OrderStatus.CONFIRMED:
            self.register_payment()
        super().save(*args, **kwargs)

    def register_payment(self):
        """
        Переводим в статус `Подтвержденный`, если заказ оплачен.
        """
        if self.gain and self.gain >= self.amount:
            self.status = OrderStatus.CONFIRMED
            self.send_client_email()
            self.send_manager_email()

    def get_absolute_url(self):
        return reverse('account:history_detail', args=[str(self.pk)])

    @property
    def amount(self):
        """
        Сумма заказа с доставкаой.
        """
        return float(self.amount_without_delivery) + float(self.delivery_price)

    @property
    def amount_without_delivery(self):
        """
        Сумма заказа без доставки.
        """
        result = 0
        for item in self.items.all():
            result += item.total_price
        return result

    @property
    def remaining_payment_sum(self):
        """
        Остаток к доплате.
        """
        return self.amount - self.gain

    @property
    def weight(self):
        """
        Вес заказа.
        """
        weight = 0
        for item in self.items.all():
            weight += item.total_weight
        return weight

    def send_client_email(self):
        """
        Отправка письма клиенту.
        """
        if self.status == OrderStatus.INWORK:
            self.send_inwork_client_email()

        elif self.status == OrderStatus.CONFIRMED:
            self.send_confirmed_client_email()

    def send_manager_email(self):
        """
        Отправка письма менеджеру.
        """
        if self.status == OrderStatus.CONFIRMED:
            self.send_confirmed_manager_email()

    def send_inwork_client_email(self):
        """
        Отправляем письмо клиенту, что его заказ в работе.
        """
        user = self.user
        if not user.email:
            return

        body_html = render_to_string(
            'orders/mail_inwork_client.html',
            {
                'site': settings.DEFAULT_DOMAIN,
                'order': self,
                'items': self.items.all(),
                'is_opt': user.groups.filter(name='Оптовик').exists(),
            }
        )

        email = create_email(
            'Заказ №%s' % self.pk,
            body_html,
            user.email
        )

        email.send()

    def send_confirmed_client_email(self):
        """
        Отправляем письмо клиенту, что его заказ подтвержден.
        """
        user = self.user
        if not user.email:
            return

        body_html = render_to_string(
            'orders/mail_confirmed_client.html',
            {
                'site': settings.DEFAULT_DOMAIN,
                'order': self,
                'items': self.items.all(),
                'is_opt': user.groups.filter(name='Оптовик').exists(),
            }
        )

        email = create_email(
            'Ваш заказ подтвержден',
            body_html,
            user.email
        )

        email.send()

    def send_confirmed_manager_email(self):
        """
        Отправляем письмо менеджеру, что заказ клиента подтвержден.
        """
        body_html = render_to_string(
            'orders/mail_confirmed_manager.html',
            {
                'user': self.user,
                'site': settings.DEFAULT_DOMAIN,
                'order': self,
                'items': self.items.all(),
            }
        )

        email = create_email(
            'Заказ №%s с сайта' % self.pk,
            body_html,
            settings.EMAIL_OPT
        )

        email.send()


class Item(models.Model):
    """
    Товар в заказе.
    """
    order = models.ForeignKey(
        'orders.Order',
        verbose_name='заказ',
        on_delete=models.CASCADE)
    offer = models.ForeignKey(
        'odinass.Offer',
        verbose_name='товар',
        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        'количество',
        default=1)
    unit_price = models.DecimalField(
        'цена за единицу',
        max_digits=12, decimal_places=2)

    class Meta:
        default_related_name = 'items'
        ordering = ['offer__title']
        verbose_name = 'товар заказа'
        verbose_name_plural = 'товары заказа'

    def __str__(self):
        return str(self.offer)

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def total_weight(self):
        return self.offer.weight * self.quantity


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='пользователь',
        related_name='profile',
        on_delete=models.CASCADE)
    price_type = models.ForeignKey(
        'odinass.PriceType',
        verbose_name='тип цены',
        db_index=True, blank=True, null=True)
    company = models.CharField(
        'компания',
        max_length=254, blank=True)
    company_address = models.TextField(
        'юридический адрес',
        blank=True)
    inn = models.CharField(
        'ИНН',
        max_length=254, blank=True)
    phone = models.CharField(
        'телефон',
        max_length=254, blank=True)

    class Meta:
        default_related_name = 'profiles'
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return self.user.username


class GroupSettings(models.Model):
    group = models.OneToOneField(
        Group,
        verbose_name='группа',
        related_name='settings',
        on_delete=models.CASCADE)
    email = models.EmailField(
        'почта',
        max_length=254, blank=True)

    class Meta:
        default_related_name = 'group_settings'
        verbose_name = 'настройка групп'
        verbose_name_plural = 'настройки групп'

    def __str__(self):
        return self.group.name


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(post_save, sender=Group)
def create_or_update_group_settings(sender, instance, created, **kwargs):
    if created:
        GroupSettings.objects.create(group=instance)
    instance.settings.save()


@receiver(payment_done, sender=Payment)
def update_order_gain(sender, instance, **kwargs):
    order = Order.objects.get(pk=instance.order_id)
    order.gain = order.gain or 0 + instance.amount
    order.save()


class Office(models.Model):
    """
    Модель `Офис`.
    """
    title = models.CharField(
        'название',
        max_length=254)
    address = models.TextField(
        'адрес')
    phone = models.CharField(
        'телефон',
        max_length=254, blank=True)
    email = models.EmailField(
        'email',
        max_length=254, blank=True)
    coordinates = YandexPointField(
        'координаты',
        blank=True, null=True)
    order = models.PositiveIntegerField(
        'порядок',
        default=0)
    is_published = models.BooleanField(
        'опубликовано',
        default=True)

    class Meta:
        verbose_name = 'офис'
        verbose_name_plural = 'офисы'
        ordering = ['order']

    def __str__(self):
        return self.title

    @property
    def yandexmap_coords(self):
        return '[{0}, {1}]'.format(self.coordinates.y, self.coordinates.x)
