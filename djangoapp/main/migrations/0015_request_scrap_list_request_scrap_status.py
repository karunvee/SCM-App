# Generated by Django 5.0.1 on 2024-04-09 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_remove_request_scrap_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='scrap_list',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='scrap_status',
            field=models.BooleanField(default=True),
        ),
    ]
