# Generated by Django 5.0.1 on 2024-07-16 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_rename_self_service_component_self_pickup_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='scrap_status',
            field=models.BooleanField(default=False),
        ),
    ]