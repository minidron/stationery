# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-25 16:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_auto_20181125_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='цена доставки'),
        ),
    ]