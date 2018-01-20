from django.conf import settings
from django.db import models


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
