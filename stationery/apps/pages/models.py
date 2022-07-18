""" from msilib.schema import Class """
from operator import mod
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from ckeditor.fields import RichTextField


class Page(models.Model):
    title = models.CharField(
        'название',
        max_length=254)

    slug = models.SlugField(
        'slug',
        allow_unicode=True, blank=True)

    icon = models.CharField(
        'иконка',
        max_length=254, blank=True)

    content = RichTextField(
        'контент',
        blank=True)
    
    in_menu = models.BooleanField(verbose_name='Закрепить в основное меню', default=False)

    order = models.PositiveIntegerField(
        default=0, blank=False, null=False)
    
    page = models.ForeignKey('MenuPage', related_name='page', on_delete=models.CASCADE, verbose_name='Вкладка меню', blank=True, null=True)

    class Meta:
        default_related_name = 'pages'
        ordering = ['order']
        verbose_name = 'страница'
        verbose_name_plural = 'страницы'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.autoslug()
        super().save(*args, **kwargs)

    def autoslug(self):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)


class MenuPage(models.Model):
    title = models.CharField(
        'название вкладки',
        max_length=254, unique=True)
    sort = models.SmallIntegerField(verbose_name='Сортировка')

    class Meta:
            verbose_name = 'Вкладка страницы'
            verbose_name_plural = 'Вкладки страниц'
    
    def __str__(self):
        return self.title

class Blog(models.Model):
    title = models.CharField(
        'название',
        max_length=254)
    content = RichTextField(
        'контент',
        blank=True)
    created = models.DateTimeField(
        'дата создания',
        default=timezone.now)
    updated = models.DateTimeField(
        'дата изменения',
        editable=False, auto_now=True)

    class Meta:
        default_related_name = 'blogs'
        ordering = ['-created']
        verbose_name = 'блог'
        verbose_name_plural = 'блоги'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pages:blog_detail', args=[str(self.id)])


class Slider(models.Model):
    title = models.CharField(
        'название',
        max_length=254)
    image = models.ImageField(
        'изображене',
        upload_to='slider/')
    background = models.CharField(
        'фон',
        max_length=10, default='#2C7FAE')
    content = models.TextField(
        'текст', blank=True)
    discount = models.CharField(
        'скидка',
        max_length=254, blank=True)
    url = models.CharField(
        'ссылка на страницу',
        max_length=254, blank=True)
    order = models.PositiveIntegerField(
        default=0, blank=False, null=False)

    class Meta:
        default_related_name = 'slides'
        ordering = ['order']
        verbose_name = 'слайд'
        verbose_name_plural = 'слайды'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Vkvidjet(models.Model):
    title = models.CharField(
        'Название',
        max_length=100, blank=True)
    url = models.CharField(
        'Cсылка на страницу',
        max_length=254, blank=True)
    script = models.TextField(
        'Скрипт', blank=True)
    status = models.BooleanField(
        'На все страницы', blank=True, default=False, help_text='Если есть другие активные виджеты, то необходимо отключить данный параметр')

    class Meta:
        verbose_name = 'Вк виджет'
        verbose_name_plural = 'Вк виджеты'

    def __str__(self):
        return self.title

class FooterImg(models.Model):
    COLOR = [
        ("Футер", "Футер"),
    ]
    title = models.CharField(max_length=10,choices=COLOR,unique=True,default="Футер")
    color = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Изменение футера'
        verbose_name_plural = 'Изменение футера'


    def str(self):
        return self.title

class Color(models.Model):
    COLOR = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5")
    ]

    title = models.CharField(max_length=10,choices=COLOR,unique=True)
    color = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Цвет для полоски под меню'
        verbose_name_plural = 'Цвет для полоски под меню'

    def __str__(self):
        return self.title

class SocialLink(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    sort = models.SmallIntegerField(unique=True, verbose_name='Порядок сортировки')
    social = models.CharField(max_length=150, verbose_name='Код иконки')
    link = models.CharField(max_length=200, verbose_name='Ссылка')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Социальные иконки в футере'
        verbose_name_plural = 'Социальные иконки в футере'
    

class HeaderLogo(models.Model):
    LOGO = [
        ('Логотип', 'Логотип')
    ]

    title = models.CharField(max_length=20, choices=LOGO, unique=True, verbose_name='Название')
    img = models.ImageField(upload_to='slider/', verbose_name='Изображение')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Логотип'
        verbose_name_plural = 'Логотип'

class ImgCategory(models.Model):
    COLOR = [
        ("1 Левый верх", "Левый верх"),
        ("2 Правый верх", "Правый верх"),
        ("3 Левый низ", "Левый низ"),
        ("4 Правый низ", "Правый низ"),
    ]

    title = models.CharField(max_length=20, choices=COLOR, verbose_name='Название',unique=True)
    img = models.ImageField(upload_to="slider/", verbose_name='Картинка')
    video = models.FileField(upload_to="slider/", verbose_name='Видео',blank=True)

    class Meta:
        verbose_name = 'Картинки и видео для основных категорий'
        verbose_name_plural = 'Картинки и видео для основных категорий'
        ordering = ['title']

    def __str__(self):
        return self.title

class ColorTopHead(models.Model):
   

    title = models.CharField(max_length=15,unique=True)
    color = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Цвет полоски меню'
        verbose_name_plural = 'Цвет полоски меню'

    def __str__(self):
        return self.title
