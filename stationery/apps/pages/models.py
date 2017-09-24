from django.db import models
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
