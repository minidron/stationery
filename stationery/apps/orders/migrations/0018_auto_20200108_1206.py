# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-08 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_auto_20181127_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_type',
            field=models.IntegerField(choices=[(1, 'Самовывоз'), (2, 'Почта России')], default=1, verbose_name='тип доставки'),
        ),
    ]
