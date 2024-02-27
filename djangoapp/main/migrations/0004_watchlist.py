# Generated by Django 5.0.1 on 2024-02-21 02:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rename_member_historytrading_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('warning_period', models.IntegerField(default=7)),
                ('alert_period', models.IntegerField(default=14)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('serial_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.serialnumber')),
            ],
        ),
    ]
