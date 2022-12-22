# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-22 12:31
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Count

from accounts.utils import normalize_email


def remove_with_empty_email(apps, schema_editor):
    """
    Удаляем пользователей с пустым email.
    """
    User = apps.get_model('accounts', 'User')
    User.objects.filter(email='').delete()


def email_to_lowercase(apps, schema_editor):
    """
    Переводим email в нижний регистр.
    """
    User = apps.get_model('accounts', 'User')

    for user in User.objects.all():
        user.email = normalize_email(user.email)
        user.save()


def removing_duplicates(apps, schema_editor):
    """
    Удаляем дубликаты пользователей (с одинаковым email).
    """
    User = apps.get_model('accounts', 'User')
    Order = apps.get_model('orders', 'Order')

    emails = (
        User.objects
        .values('email')
        .annotate(duplicate=Count('email'))
        .filter(duplicate__gt=1)
        .values_list('email', flat=True))

    for email in emails:
        users = User.objects.filter(email=email)
        main_user = users.latest('last_login')
        Order.objects.filter(user__in=users).update(user=main_user)
        users.exclude(id=main_user.id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_rename_user_table'),
    ]

    operations = [
        migrations.RunPython(
            remove_with_empty_email,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            email_to_lowercase,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            removing_duplicates,
            reverse_code=migrations.RunPython.noop
        ),
    ]
