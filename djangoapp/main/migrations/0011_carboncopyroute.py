# Generated by Django 5.0.1 on 2025-03-06 03:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20250116_0829'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarbonCopyRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approve_route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carbon_copy_route', to='main.approvedroute')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cc_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
