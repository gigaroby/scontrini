# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_receipt_price_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='selected_price',
            field=models.IntegerField(null=True),
        ),
    ]