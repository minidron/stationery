import uuid

from django.conf import settings
from django.db import models
from django.db.models import (
    Case, F, IntegerField, OuterRef, Prefetch, Subquery, Sum, Value, When)
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from ckeditor.fields import RichTextField
from django_resized import ResizedImageField
from mptt.models import MPTTModel, TreeForeignKey
from pytils.translit import slugify

from lib.email import create_email
from odinass.utils import remove_specialcharacters


def generate_upload_path(instance, filename):
    filename = '{name}.{ext}'.format(name=uuid.uuid4().hex,
                                     ext=instance.image_format)
    return '{folder}/{file}'.format(folder=instance.image_folder,
                                    file=filename)


class Category(MPTTModel):
    """
    Категория товаров
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'название',
        max_length=254, db_index=True)
    slug = models.SlugField(
        'slug',
        blank=True, max_length=254)
    path = models.TextField(
        'полный путь',
        null=True, blank=True, db_index=True)
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
    order = models.PositiveIntegerField(
        default=0, blank=False, null=False)
    content = RichTextField(
        'описание',
        blank=True, default='')
    views = models.IntegerField(
        'кол-во просмотров',
        default=0)
    metatitle = models.TextField(
        'Тайтл',
        max_length=200,
        blank=True, null=True)
    description = models.TextField(
        'Дескрипшен',
        max_length=300,
        blank=True, null=True)
    h1_title = models.TextField(
        'H1 тэг',
        max_length=200,
        blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        default_related_name = 'categories'
        ordering = ['order']
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.autoslug()
        self.path = self.get_path()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pages:catalog', kwargs={'path': self.path})

    def get_path(self):
        """
        Полный путь к категории.
        """
        created = not self._state.adding
        if created:
            slugs = (self.get_ancestors(ascending=False, include_self=True)
                         .values_list('slug', flat=True))
        else:
            slug_list = []
            instance = self
            while instance is not None:
                slug_list.append(instance.slug)
                instance = instance.parent
            slugs = reversed(slug_list)
        return '/'.join(slugs)

    def offers(self, user=None):
        return Offer.objects.offers(user=user, category=self)

    def autoslug(self):
        if self.slug:
            return
        self.slug = slugify(self.title.strip())


class Warehouse(models.Model):
    """
    Склад
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'название',
        max_length=254, db_index=True)
    is_selected = models.BooleanField(
        'выбрано',
        default=False)

    class Meta:
        default_related_name = 'warehouses'
        ordering = ['title']
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return self.title


class Rest(models.Model):
    """
    Остаток
    """
    value = models.IntegerField(
        'остаток',
        default=0)
    warehouse = models.ForeignKey(
        'odinass.Warehouse',
        verbose_name='склад')
    offer = models.ForeignKey(
        'odinass.Offer',
        verbose_name='предложение')

    class Meta:
        default_related_name = 'rests'
        verbose_name = 'остаток'
        verbose_name_plural = 'остатки'

    def __str__(self):
        return str(self.value)


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
    is_weight = models.BooleanField(
        'используется для веса',
        default=False)

    class Meta:
        default_related_name = 'properties'
        ordering = ['title']
        verbose_name = 'свойство'
        verbose_name_plural = 'свойства'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_weight:
            (Property.objects.exclude(pk=self.pk)
                             .filter(is_weight=True)
                             .update(is_weight=False))
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Товар
    """
    image_folder = 'products'
    image_format = 'jpg'

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'название', max_length=508)
    search_title = models.CharField(
        'название для поиска',
        default='',
        max_length=500, blank=True)
    article = models.CharField(
        'артикул', blank=True, max_length=254)
    category = models.ForeignKey(
        'odinass.Category',
        verbose_name='категория',
        blank=True, null=True)
    property_values = models.ManyToManyField(
        'odinass.PropertyValue',
        verbose_name='значения свойства',
        blank=True)
    image = ResizedImageField(
        'изображение',
        size=[1024, 1024], upload_to=generate_upload_path, force_format='JPEG',
        null=True, blank=True)
    created = models.DateField(
        'дата создания',
        auto_now_add=True, editable=False, null=False, blank=False)
    is_favorite = models.BooleanField(
        'избранный',
        db_index=True, default=False)
    content = RichTextField(
        'описание',
        blank=True, default='')
    new_price = models.DecimalField(
        'Старая цена',
        max_digits=12, decimal_places=2,
        blank=True, null=True)
    stock = models.TextField(
        'Условия акции',
        max_length=200,
        blank=True, null=True)

    class Meta:
        default_related_name = 'products'
        ordering = ['title']
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.search_title = remove_specialcharacters(self.title)
        super().save(*args, **kwargs)

        order = getattr(self, 'order', None)
        if self.is_favorite and not order:
            ProductOrder.objects.create(
                product=self, order=ProductOrder.next_order())

        elif not self.is_favorite and order:
            order.delete()


class ProductOrder(models.Model):
    """
    Новинки.
    """
    product = models.OneToOneField(
        'odinass.Product',
        verbose_name='товар',
        related_name='order',
        on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        'порядок',
        default=0, blank=False, null=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'новинка'
        verbose_name_plural = 'новинки'

    def __str__(self):
        return str(self.product)

    @classmethod
    def next_order(cls):
        last_product = cls.objects.last()
        if last_product:
            return last_product.order + 1
        return 0


@receiver(post_delete, sender=ProductOrder)
def disable_is_favorite(sender, instance, **kwargs):
    """
    Ставим is_favorite в False, когда удаляем сортировку у этого товара.
    """
    product = instance.product
    product.is_favorite = False
    product.order = None
    product.save()


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
        ordering = ['property__title', 'title']
        verbose_name = 'значение свойства'
        verbose_name_plural = 'значения свойства'

    def __str__(self):
        return self.title


class PriceType(models.Model):
    """
    Тип цены
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'наименование',
        max_length=254)
    is_default = models.BooleanField(
        'по умолчанию',
        db_index=True, default=False)

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


class OfferQuerySet(models.QuerySet):
    def offers(self, user=None, category=None, ids=None):
        price_params = {}
        if user and hasattr(user, 'price_type') and user.price_type:
            price_params['price_type'] = user.price_type
        else:
            price_params['price_type__is_default'] = True

        price = Price.objects.filter(offer=OuterRef('pk'), **price_params)

        # остатки по нужным складам
        prefetch = Prefetch(
            'rests', queryset=Rest.objects.filter(warehouse__is_selected=True)
                                          .order_by('warehouse__title'))

        offer_params = {}
        if category:
            offer_params['product__category'] = category
        if ids:
            offer_params['pk__in'] = ids

        return (Offer.objects
                     .select_related('product')
                     .prefetch_related('prices', 'prices__price_type',
                                       prefetch, 'rests__warehouse',
                                       'product__property_values',
                                       'product__property_values__property')
                     .filter(**offer_params)
                     .annotate(
                        retail_price=Subquery(price.values('price')[:1]),
                        rests_count=Sum(Case(
                            When(rests__warehouse__is_selected=True,
                                 then=F('rests__value')),
                            When(rests__value__gte=0, then=F('rests__value')),
                            default=Value(0),
                            output_field=IntegerField()
                        ))))


class Offer(models.Model):
    """
    Предложение
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        'наименование',
        max_length=254)
    description = models.TextField(
        'Дескрипшен',
        max_length=300,
        blank=True, null=True)
    keywords = models.TextField(
        'Ключевые слова',
        max_length=500,
        blank=True, null=True)
    slug = models.SlugField(
        'slug',
        blank=True, max_length=254)
    product = models.ForeignKey(
        'odinass.Product',
        verbose_name='товар')

    objects = OfferQuerySet.as_manager()

    class Meta:
        default_related_name = 'offers'
        ordering = ['title']
        verbose_name = 'предложение'
        verbose_name_plural = 'предложения'

    def __str__(self):
        return self.full_title

    def save(self, *args, **kwargs):
        self.autoslug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        path = '/'.join([self.product.category.path, self.slug])
        return reverse('pages:catalog', kwargs={'path': path})

    def get_absolute_tags(self):
        tag = self.slug
        path = '/'.join([self.product.category.path, self.title])
        return reverse('pages:catalog', kwargs={'path': path, 'tag': tag})

    def autoslug(self):
        if self.slug:
            return
        self.slug = slugify(self.title)

    def price(self, user=None):
        price_params = {}
        if user and hasattr(user, 'price_type') and user.price_type:
            price_params['price_type'] = user.price_type
        else:
            price_params['price_type__is_default'] = True

        try:
            qs = self.prices.get(**price_params)
            price = qs.price
        except Price.DoesNotExist:
            price = 0

        return price

    @property
    def features(self):
        return (PropertyValue.objects
                             .filter(product=self.product))

    @property
    def rest_list(self):
        return (Rest.objects.filter(warehouse__is_selected=True, offer=self)
                            .order_by('warehouse__title'))

    @property
    def rest_limit(self):
        return self.rest_list.aggregate(total=Sum('value'))['total']

    @property
    def full_title(self):
        return self.product.title

    @property
    def weight(self):
        """
        Возвращает вес в граммах.
        """
        try:
            weight = self.product.property_values.get(
                property__is_weight=True).title
            weight = "".join(weight.split())

            is_gr = False
            is_kilo = False
            normalized_weight = ''
            for s in weight:
                if s.isdigit():
                    normalized_weight += s
                elif s == '.':
                    normalized_weight += s
                elif s == ',':
                    normalized_weight += '.'
                else:
                    if s.lower() == 'г':
                        is_gr = True
                    elif s.lower() == 'к':
                        is_kilo = True
                    break

            if not any([is_gr, is_kilo]):
                return 0

            try:
                weight = float(normalized_weight)
                if is_kilo:
                    weight = weight * 1000
            except ValueError:
                return 0

            return weight
        except PropertyValue.DoesNotExist:
            return 0


class Tags(models.Model):
    """
    Тэги товара
    """
    tegs = models.CharField(
        'Тэги товара',
        max_length=100)
    offer = models.ForeignKey(
        Offer,
        verbose_name='Предложение товара',
        on_delete=models.CASCADE,
        related_name='offer_tags')


class ActionLog(object):
    """
    Список операций для логирования
    """
    IMPORT = 1
    EXPORT = 2

    CHOICES = (
        (IMPORT, 'импорт'),
        (EXPORT, 'экспорт'),
    )

    CHOICES_MACHINE_NAME = {
        IMPORT: 'import',
        EXPORT: 'export',
    }


class StatusLog(object):
    """
    Список статусов для логирования
    """
    PROGRESS = 1
    FINISHED = 2
    FAILD = 3

    CHOICES = (
        (PROGRESS, 'обрабатывается'),
        (FINISHED, 'завершено'),
        (FAILD, 'завершено с ошибкой'),
    )

    CHOICES_MACHINE_NAME = {
        PROGRESS: 'progress',
        FINISHED: 'finished',
        FAILD: 'faild',
    }


class Log(models.Model):
    """
    Логирование импорта и экспорта с 1С
    """
    action = models.IntegerField(
        'действие',
        choices=ActionLog.CHOICES, blank=True, null=True)

    status = models.IntegerField(
        'статус',
        choices=StatusLog.CHOICES, default=StatusLog.PROGRESS)

    filename = models.CharField(
        'название файла',
        max_length=254, db_index=True)

    created = models.DateTimeField(
        'время создания',
        auto_now_add=True, editable=False, null=False, blank=False)

    traceback = models.TextField(
        'traceback',
        blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'лог'
        verbose_name_plural = 'логи'

    def __str__(self):
        return str(self.created)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.status == StatusLog.FAILD:
            email = create_email(
                'Ошибка выгрузки на сайт',
                render_to_string('odinass/email/error_import_current.html', {
                    'log': self,
                }),
                settings.EMAIL_OPT
            )
            email.send()
