# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2021-03-25 05:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_ordergoods_specs'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderinfo',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='逻辑删除'),
        ),
    ]
