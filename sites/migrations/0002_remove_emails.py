# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-23 20:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='email',
        ),
        migrations.RemoveField(
            model_name='site',
            name='publish_email',
        ),
    ]
