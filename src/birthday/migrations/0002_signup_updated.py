# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-04 01:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('birthday', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='updated',
            field=models.DateTimeField(blank=True, default=django.utils.datetime_safe.datetime.now),
        ),
    ]