# Generated by Django 5.0.1 on 2025-06-11 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_remove_shiftduty_shift_shiftdutyrelative_shift'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='lineId',
            new_name='line_id',
        ),
    ]
