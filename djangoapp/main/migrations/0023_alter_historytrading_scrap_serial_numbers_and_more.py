# Generated by Django 5.0.1 on 2024-04-19 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_historytrading_scrap_serial_numbers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historytrading',
            name='scrap_serial_numbers',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='historytrading',
            name='serial_numbers',
            field=models.TextField(default=''),
        ),
    ]