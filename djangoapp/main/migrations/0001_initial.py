# Generated by Django 5.0.1 on 2024-03-05 12:02

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='PO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po_number', models.CharField(blank=True, max_length=250)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('emp_id', models.CharField(max_length=10, unique=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('department', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_user', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_supervisor', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_numbers', models.TextField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('name', models.CharField(max_length=250)),
                ('model', models.CharField(max_length=250)),
                ('description', models.CharField(blank=True, max_length=250)),
                ('supplier', models.CharField(blank=True, max_length=250)),
                ('quantity', models.IntegerField()),
                ('quantity_warning', models.IntegerField(default=20)),
                ('quantity_alert', models.IntegerField(default=10)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('consumable', models.BooleanField(default=True)),
                ('component_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.componenttype')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.department')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.location')),
            ],
        ),
        migrations.CreateModel(
            name='HistoryTrading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_numbers', models.TextField()),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.component')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderTacking',
            fields=[
                ('status', models.CharField(choices=[('Processing', 'Processing'), ('PR', 'PR'), ('PO', 'PO'), ('Shipping', 'Shipping'), ('Good Received', 'Good Received'), ('In-House', 'In-House')], default='Processing', max_length=255)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pr_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('po_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('shipping_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('receive_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('po', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='main.po')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('staff_approved', models.CharField(blank=True, max_length=255)),
                ('supervisor_approved', models.CharField(blank=True, max_length=255)),
                ('order_ready', models.BooleanField(default=False)),
                ('serial_numbers', models.TextField()),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('complete_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SerialNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=100, unique=True)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='serial_numbers', to='main.component')),
                ('po', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.po')),
            ],
        ),
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
