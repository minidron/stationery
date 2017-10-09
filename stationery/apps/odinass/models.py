import uuid

from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


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
