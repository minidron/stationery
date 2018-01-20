from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


UserModel = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Cart(models.Model):
    """
    Корзина пользователя.
    """
    is_complete = models.BooleanField(
        'завершено',
        default=False)

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'

    def __str__(self):
        return str(self.pk)


class Profile(models.Model):
    """
    Профиль пользователя.
    """
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE)
    cart = models.OneToOneField(
        'orders.Cart',
        verbose_name='корзина',
        related_name='profile',
        on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return str(self.user)


class UserSession(models.Model):
    """
    Ассоциация пользователя с сессией.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL)
    session = models.ForeignKey(
        Session)

    class Meta:
        default_related_name = 'user_sessions'


def user_logged_in_handler(sender, request, user, **kwargs):
    """
    При авторизации пользователя, ассоциируем его с сессией.
    """
    UserSession.objects.get_or_create(
        user=user,
        session_id=request.session.session_key,
    )

user_logged_in.connect(user_logged_in_handler)


@receiver(post_save, sender=Cart)
def create_cart(sender, instance, created, **kwargs):
    if created:
        instance.profile.cart = instance


@receiver(post_save, sender=Cart)
def save_cart_profile(sender, instance, created, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=UserModel)
def create_user_profile(sender, instance, created, **kwargs):
    if created or not getattr(instance, 'profile', None):
        Profile.objects.create(user=instance)


@receiver(post_save, sender=UserModel)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
