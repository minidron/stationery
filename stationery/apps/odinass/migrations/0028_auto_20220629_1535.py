# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-29 12:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('odinass', '0027_offer_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=100, verbose_name='Тэги товара')),
            ],
        ),
        migrations.RemoveField(
            model_name='offer',
            name='tags',
        ),
        migrations.AddField(
            model_name='tags',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offer', to='odinass.Offer', verbose_name='Предложение товара'),
        ),
    ]
