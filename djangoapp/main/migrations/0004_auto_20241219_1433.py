# Generated by Django 3.2.18 on 2024-12-19 07:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20241115_0951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryreport',
            name='component',
        ),
        migrations.AddField(
            model_name='inventoryreport',
            name='location',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='main.location'),
            preserve_default=False,
        ),
    ]
