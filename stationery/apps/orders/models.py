from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    objects = OrderQuerySet.as_manager()

    class Meta:
        default_related_name = 'orders'
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return str(self.pk)

    @classmethod
    def get_cart(cls, user):
        """
        Получить корзину пользователя, если нет, то создать её.
        """
        cart, created = cls.objects.get_or_create(
            user=user, status=OrderStatus.NOT_CREATED)
        return cart

    def add_item(self, offer_id, quantity, user=None):
        try:
            item = Item.objects.get(order=self, offer=offer_id)
        except Item.DoesNotExist:
            item = Item(order=self, offer_id=offer_id, quantity=quantity)
        else:
            item.quantity += quantity
        item.save(user=user)

    def update_item(self, offer_id, quantity):
        try:
            item = Item.objects.get(order=self, offer=offer_id)
        except Item.DoesNotExist:
            pass
        else:
            if quantity == 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()

    def remove_item(self, offer_id):
        try:
            item = Item.objects.get(order=self, offer=offer_id)
        except Item.DoesNotExist:
            pass
        else:
            item.delete()

    @property
    def amount(self):
        result = 0
        for item in self.items.all():
            result += item.total_price
        return result


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

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.unit_price = self.get_unit_price(user)
        super().save(*args, **kwargs)
        if self.quantity == 0:
            self.delete()

    def get_unit_price(self, user=None):
        return self.offer.price(user=user)

    @property
    def total_price(self):
        return self.unit_price * self.quantity


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
    inn = models.CharField(
        'ИНН',
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
        'телефон',
        max_length=254, blank=True)
    coordinates = YandexPointField(
        'координаты',
        blank=True, null=True)
    order = models.PositiveIntegerField(
        'порядок',
        default=0)

    class Meta:
        verbose_name = 'офис'
        verbose_name_plural = 'офисы'
        ordering = ['order']

    def __str__(self):
        return self.title

    @property
    def yandexmap_coords(self):
        return '[{0}, {1}]'.format(self.coordinates.y, self.coordinates.x)
