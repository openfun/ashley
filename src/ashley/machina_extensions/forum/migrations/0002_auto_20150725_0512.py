# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="forum",
            options={
                "ordering": ["tree_id", "lft"],
                "verbose_name": "Forum",
                "verbose_name_plural": "Forums",
            },
        ),
    ]
