# Generated by Django 5.0.1 on 2024-04-09 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_rename_requester_name_request_requester_name_center_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='request',
            old_name='requester_name_emp',
            new_name='requester_emp_center',
        ),
    ]
