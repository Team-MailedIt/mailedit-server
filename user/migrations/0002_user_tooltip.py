# Generated by Django 3.1 on 2022-01-29 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tooltip',
            field=models.BooleanField(default=True),
        ),
    ]
