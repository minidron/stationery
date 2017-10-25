# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-22 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricetype',
            name='sales_type',
            field=models.IntegerField(blank=True, choices=[(1, 'розница'), (2, 'оптовая продажа')], db_index=True, null=True, unique=True, verbose_name='тип продажи'),
        ),
    ]
