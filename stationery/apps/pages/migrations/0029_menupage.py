# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-07-07 14:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0028_auto_20220523_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=254, unique=True, verbose_name='название вкладки')),
                ('sort', models.SmallIntegerField(verbose_name='Сортировка')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page', to='pages.Page', verbose_name='Вкладка меню')),
            ],
            options={
                'verbose_name': 'Вкладка страницы',
                'verbose_name_plural': 'Вкладки страниц',
            },
        ),
    ]
