# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-17 10:20
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0014_auto_20180831_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='описание'),
        ),
        migrations.AddField(
            model_name='product',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='описание'),
        ),
    ]
