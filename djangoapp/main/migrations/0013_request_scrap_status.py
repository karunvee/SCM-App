# Generated by Django 5.0.1 on 2024-04-09 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_request_requester_emp_center_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='scrap_status',
            field=models.BooleanField(default=True),
        ),
    ]