# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-11 08:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtei', '0002_auto_20190109_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='rteidocument',
            name='file_size',
            field=models.PositiveIntegerField(editable=False, null=True),
        ),
    ]
