# Generated by Django 5.0.1 on 2024-11-07 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_component_last_inventory_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='equipment_type',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
