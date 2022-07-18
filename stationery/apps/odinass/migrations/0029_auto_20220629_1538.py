# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-29 12:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0028_auto_20220629_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offer_tags', to='odinass.Offer', verbose_name='Предложение товара'),
        ),
    ]
