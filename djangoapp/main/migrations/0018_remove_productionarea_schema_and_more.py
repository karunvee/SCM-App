# Generated by Django 5.0.1 on 2025-03-26 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_equipmenttype_quantity_productionarea_schema'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productionarea',
            name='schema',
        ),
        migrations.AddField(
            model_name='productionarea',
            name='mes_factory',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='productionarea',
            name='prod_area_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
