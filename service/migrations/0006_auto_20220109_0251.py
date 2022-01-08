# Generated by Django 3.1 on 2022-01-08 17:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("service", "0005_auto_20220109_0250"),
    ]

    operations = [
        migrations.AlterField(
            model_name="block",
            name="template",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="template_blocks",
                to="service.template",
            ),
        ),
        migrations.AlterField(
            model_name="template",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, editable=False, serialize=False
            ),
        ),
    ]