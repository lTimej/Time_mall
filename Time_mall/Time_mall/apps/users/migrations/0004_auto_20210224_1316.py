# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2021-02-24 05:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210216_1605'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['-update_time'], 'verbose_name': '用户地址', 'verbose_name_plural': '用户地址'},
        ),
    ]
