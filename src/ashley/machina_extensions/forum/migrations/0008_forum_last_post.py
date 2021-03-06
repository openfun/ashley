# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-29 04:27
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forum_conversation", "0010_auto_20170120_0224"),
        ("forum", "0007_auto_20170523_2140"),
    ]

    operations = [
        migrations.AddField(
            model_name="forum",
            name="last_post",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="forum_conversation.Post",
                verbose_name="Last post",
            ),
        ),
    ]
