from django.db import models
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

    order = models.PositiveIntegerField(
        default=0, blank=False, null=False)

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
        self.autoslug()
        super().save(*args, **kwargs)

    def autoslug(self):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)


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
