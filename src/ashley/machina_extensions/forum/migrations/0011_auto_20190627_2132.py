# Generated by Django 2.2.2 on 2019-06-28 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0010_auto_20181103_1401"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forum",
            name="level",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="forum",
            name="lft",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="forum",
            name="rght",
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
