# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-30 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0022_auto_20200909_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='path',
            field=models.TextField(blank=True, db_index=True, null=True, verbose_name='полный путь'),
        ),
    ]
