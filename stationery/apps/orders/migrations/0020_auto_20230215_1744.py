# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-02-15 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_auto_20221222_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_type',
            field=models.IntegerField(choices=[(1, 'Самовывоз из пункта выдачи (Серпухов, ул. Ворошилова, 94)'), (2, 'Почта России')], default=1, verbose_name='тип доставки'),
        ),
    ]
