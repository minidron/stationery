from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import normalize_email


class CustomUserManager(BaseUserManager):
    """
    Define a model manager for User model with no username field.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        email = normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель пользователя.
    """
    username = None

    # Осн. данные
    email = models.EmailField(
        _('email address'),
        unique=True)
    phone = models.CharField(
        'телефон',
        default='',
        max_length=254,
        blank=True)

    # Настройки
    price_type = models.ForeignKey(
        'odinass.PriceType',
        verbose_name='тип цены',
        on_delete=models.SET_NULL,
        related_query_name='%(class)s',
        blank=True, null=True, db_index=True)
    is_wholesaler = models.BooleanField(
        'оптовик',
        default=False,
        help_text='Отметьте, если пользователь является оптовиком.')
    company = models.CharField(
        'компания',
        default='',
        max_length=254,
        blank=True)
    company_address = models.TextField(
        'юридический адрес',
        default='',
        blank=True)
    inn = models.CharField(
        'ИНН',
        default='',
        max_length=254,
        blank=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    class Meta:
        default_related_name = '%(class)ss'
        ordering = ['email']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
