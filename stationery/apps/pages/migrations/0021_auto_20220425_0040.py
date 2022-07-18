# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-04-24 21:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0020_auto_20220423_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imgcategory',
            name='title',
            field=models.CharField(choices=[('1 Левый верх', 'Левый верх'), ('2 Правый верх', 'Правый верх'), ('3 Левый низ', 'Левый низ'), ('4 Правый низ', 'Правый низ')], max_length=20, unique=True, verbose_name='Название'),
        ),
    ]
