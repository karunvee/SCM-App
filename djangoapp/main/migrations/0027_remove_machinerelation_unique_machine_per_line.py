# Generated by Django 5.0.1 on 2025-07-11 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_remove_component_equipment_type_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='machinerelation',
            name='unique_machine_per_line',
        ),
    ]
