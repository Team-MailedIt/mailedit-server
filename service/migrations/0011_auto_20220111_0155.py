# Generated by Django 3.1 on 2022-01-10 16:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0010_auto_20220111_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='basetemplate',
            name='category',
            field=models.CharField(choices=[('회사', '회사'), ('학교', '학교')], default='회사', max_length=6),
        ),
        migrations.AlterField(
            model_name='group',
            name='color',
            field=models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(code='nomatch', message='Length has to be 7', regex='^.{7}$')]),
        ),
    ]