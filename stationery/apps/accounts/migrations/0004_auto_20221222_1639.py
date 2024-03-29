# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-22 13:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0036_auto_20221102_1804'),
        ('accounts', '0003_prepare_accounts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['email'], 'verbose_name': 'пользователь', 'verbose_name_plural': 'пользователи'},
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.CharField(blank=True, default='', max_length=254, verbose_name='компания'),
        ),
        migrations.AddField(
            model_name='user',
            name='company_address',
            field=models.TextField(blank=True, default='', verbose_name='юридический адрес'),
        ),
        migrations.AddField(
            model_name='user',
            name='inn',
            field=models.CharField(blank=True, default='', max_length=254, verbose_name='ИНН'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_wholesaler',
            field=models.BooleanField(default=False, help_text='Отметьте, если пользователь является оптовиком.', verbose_name='оптовик'),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=254, verbose_name='телефон'),
        ),
        migrations.AddField(
            model_name='user',
            name='price_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', related_query_name='user', to='odinass.PriceType', verbose_name='тип цены'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
