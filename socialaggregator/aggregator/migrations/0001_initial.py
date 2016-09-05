# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-11 10:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('default', '0004_auto_20160423_0400'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialPerson',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=64)),
                ('avatar_url', models.URLField()),
                ('email', models.EmailField(max_length=254, null=True)),
                ('provider', models.CharField(max_length=32)),
                ('social_person_type', models.CharField(choices=[
                 (b'friend', b'friend'), (b'follower', b'follower')], max_length=9)),
                ('user_social_auth', models.ManyToManyField(
                    to='default.UserSocialAuth')),
            ],
        ),
    ]
