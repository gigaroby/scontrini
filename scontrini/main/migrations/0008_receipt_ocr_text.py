# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 20:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_receipt_selected_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='ocr_text',
            field=models.CharField(blank=True, max_length=40000),
        ),
    ]