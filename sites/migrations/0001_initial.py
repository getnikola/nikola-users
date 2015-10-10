# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Display name', unique=True)),
                ('language_code', models.CharField(max_length=5, verbose_name='Language code')),
                ('country_code', models.CharField(max_length=5, verbose_name='Country code')),
                ('display_country', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('url', models.URLField(max_length=512, verbose_name='Site URL', unique=True)),
                ('author', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('description', models.TextField(max_length=512)),
                ('sourcelink', models.URLField(max_length=512, verbose_name='Source link', blank=True)),
                ('date', models.DateTimeField(verbose_name='Date added', auto_now_add=True)),
                ('visible', models.BooleanField(default=False)),
                ('publish_email', models.BooleanField(verbose_name='Publish e-mail', default=False)),
                ('featured', models.BooleanField(default=False)),
                ('featured_order', models.IntegerField(verbose_name='Order (for featured sites)', null=True, blank=True)),
                ('featured_reason', models.TextField(max_length=100, verbose_name='Reason (for featured sites)', blank=True)),
                ('languages', models.ManyToManyField(to='sites.Language')),
            ],
        ),
    ]
