# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-28 09:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0024_auto_20220425_0040'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='description',
            field=models.TextField(blank=True, max_length=300, null=True, verbose_name='Дескрипшон'),
        ),
    ]