# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-24 20:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('odinass', '0006_product_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='количество')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='цена за единицу')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='odinass.Offer', verbose_name='товар')),
            ],
            options={
                'verbose_name_plural': 'товары заказа',
                'verbose_name': 'товар заказа',
                'default_related_name': 'items',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'не создан'), (2, 'в работе'), (3, 'подтвержденный'), (4, 'доставка'), (5, 'завершенный'), (6, 'аннулированный')], db_index=True, default=1, verbose_name='статус')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name_plural': 'заказы',
                'verbose_name': 'заказ',
                'default_related_name': 'orders',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.Order', verbose_name='заказ'),
        ),
    ]