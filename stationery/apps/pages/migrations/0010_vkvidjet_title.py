# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-31 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_vkvidjet'),
    ]

    operations = [
        migrations.AddField(
            model_name='vkvidjet',
            name='title',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название'),
        ),
    ]