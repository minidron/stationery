# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-27 19:10
from __future__ import unicode_literals

from django.db import migrations, models, transaction

from pytils.translit import slugify


def gen_slug(apps, schema_editor):
    Offer = apps.get_model('odinass', 'offer')
    while Offer.objects.filter(slug__isnull=True).exists():
        with transaction.atomic():
            for row in Offer.objects.filter(slug__isnull=True)[:1000]:
                row.slug = slugify(row.title)
                row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0020_category_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='slug',
            field=models.SlugField(blank=True, max_length=254, null=True, verbose_name='slug'),
        ),
        migrations.RunPython(gen_slug, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='offer',
            name='slug',
            field=models.SlugField(blank=True, max_length=254, verbose_name='slug'),
        )
    ]
