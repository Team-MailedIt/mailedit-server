# Generated by Django 3.1 on 2022-01-08 17:48

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("service", "0003_group"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="basetemplate",
            name="sub_id",
        ),
        migrations.AlterField(
            model_name="basetemplate",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, editable=False, serialize=False
            ),
        ),
    ]
