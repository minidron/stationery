# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-09 17:55
from __future__ import unicode_literals

import re

from django.db import migrations, models, transaction

from odinass.utils import remove_specialcharacters


def gen_search_title(apps, schema_editor):
    Product = apps.get_model('odinass', 'product')
    qs = Product.objects.filter(search_title='')
    while qs.exists():
        with transaction.atomic():
            for row in qs[:1000]:
                row.search_title = remove_specialcharacters(row.title)
                row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0021_offer_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='search_title',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='название для поиска'),
        ),
        migrations.RunPython(gen_search_title, reverse_code=migrations.RunPython.noop),
    ]
