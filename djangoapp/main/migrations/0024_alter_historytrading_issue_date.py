# Generated by Django 5.0.1 on 2024-04-19 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_alter_historytrading_scrap_serial_numbers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historytrading',
            name='issue_date',
            field=models.DateTimeField(),
        ),
    ]