# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-11-02 15:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0035_category_h1_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='h1_title',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='H1 тэг'),
        ),
    ]
