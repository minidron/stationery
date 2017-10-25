import uuid

from django.db import models
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey

from odinass.utils import format_price


class Category(MPTTModel):
    """
    Категория товаров
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'название',
        max_length=254, db_index=True)
    parent = TreeForeignKey(
        'self',
        verbose_name='родительская категория',
        related_name='children',
        null=True, blank=True, db_index=True)
    is_published = models.BooleanField(
        'опубликовано',
        default=True)
    image = models.ImageField(
        'изображене',
        upload_to='category/', null=True, blank=True)

    class Meta:
        default_related_name = 'categories'
        ordering = ['title']
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:category', args=[str(self.id)])

    @property
    def offers(self):
        return (Offer.objects.select_related('product')
                             .filter(product__categories=self))


class Product(models.Model):
    """
    Товар
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        'название', max_length=254)

    article = models.CharField(
        'артикул', blank=True, max_length=254)

    categories = models.ManyToManyField(
        'odinass.Category',
        verbose_name='категории',
        blank=True)

    property_values = models.ManyToManyField(
        'odinass.PropertyValue',
        verbose_name='значения свойства',
        blank=True)

    class Meta:
        default_related_name = 'products'
        ordering = ['title']
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.title


class Property(models.Model):
    """
    Свойство
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'название',
        max_length=254)
    value_type = models.CharField(
        'тип значений',
        max_length=254, blank=True)

    class Meta:
        default_related_name = 'properties'
        ordering = ['title']
        verbose_name = 'свойство'
        verbose_name_plural = 'свойства'

    def __str__(self):
        return self.title


class PropertyValue(models.Model):
    """
    Справочник
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'название',
        max_length=254)
    property = models.ForeignKey(
        'odinass.Property',
        verbose_name='свойство')

    class Meta:
        default_related_name = 'property_values'
        ordering = ['title']
        verbose_name = 'значение свойства'
        verbose_name_plural = 'значения свойства'

    def __str__(self):
        return self.title


class SalesType(object):
    """
    Тип продажи
    """
    RETAIL = 1
    WHOLESALE = 2

    CHOICES = (
        (RETAIL, 'розница'),
        (WHOLESALE, 'оптовая продажа'),
    )

    CHOICES_MACHINE_NAME = {
        RETAIL: 'retail',
        WHOLESALE: 'wholesale',
    }


class PriceType(models.Model):
    """
    Тип цены
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'наименование',
        max_length=254)
    sales_type = models.IntegerField(
        'тип продажи',
        choices=SalesType.CHOICES, db_index=True, blank=True, null=True,
        unique=True)

    class Meta:
        default_related_name = 'price_types'
        ordering = ['title']
        verbose_name = 'тип цены'
        verbose_name_plural = 'тип цен'

    def __str__(self):
        return self.title


class Price(models.Model):
    """
    Цены
    """
    currency = models.CharField(
        'валюта',
        max_length=254)
    price = models.DecimalField(
        'цена',
        max_digits=12, decimal_places=2)
    price_type = models.ForeignKey(
        'odinass.PriceType',
        verbose_name='тип цены')
    offer = models.ForeignKey(
        'odinass.Offer',
        verbose_name='предложение')

    class Meta:
        default_related_name = 'prices'
        ordering = ['currency']
        verbose_name = 'цена'
        verbose_name_plural = 'цены'

    def __str__(self):
        price = 'нет цены'
        if self.price:
            price = '%s %s' % (self.price, self.currency)
        return price


class Offer(models.Model):
    """
    Предложение
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'наименование', max_length=254)
    product = models.ForeignKey(
        'odinass.Product',
        verbose_name='товар')

    class Meta:
        default_related_name = 'offers'
        ordering = ['title']
        verbose_name = 'предложение'
        verbose_name_plural = 'предложения'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:product', args=[str(self.id)])

    @property
    def price(self):
        price = self.prices.filter(price_type__sales_type=SalesType.RETAIL)
        if len(price):
            price = price.first()
        else:
            return 'нет цены'
        return '%s %s' % (format_price(price.price), price.currency)

    @property
    def features(self):
        return (PropertyValue.objects
                             .filter(product=self.product))
