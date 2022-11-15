# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-30 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_auto_20180422_2323'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vkvidjet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(blank=True, max_length=254, verbose_name='Cсылка на страницу')),
                ('script', models.TextField(blank=True, verbose_name='Скрипт')),
            ],
            options={
                'verbose_name': 'Вк виджет',
                'verbose_name_plural': 'Вк виджеты',
            },
        ),
    ]