# Generated by Django 5.0.1 on 2024-03-21 03:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_remove_request_serial_numbers_serialnumber_request_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serialnumber',
            name='request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.request'),
        ),
    ]
