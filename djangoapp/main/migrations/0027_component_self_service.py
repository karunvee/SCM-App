# Generated by Django 5.0.1 on 2024-07-16 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_component_last_sn'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='self_service',
            field=models.BooleanField(default=False),
        ),
    ]