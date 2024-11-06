# Generated by Django 5.0.1 on 2024-11-06 06:47

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='last_inventory_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='component',
            name='next_inventory_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='InventoryReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('Abnormal', 'Abnormal'), ('Normal', 'Normal')], default='Abnormal', max_length=255)),
                ('inventory_date', models.DateTimeField(auto_now_add=True)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.component')),
            ],
        ),
    ]
