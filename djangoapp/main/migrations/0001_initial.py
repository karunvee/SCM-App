# Generated by Django 3.2.18 on 2024-11-05 12:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import main.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
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
                ('is_center', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('name', models.CharField(max_length=250)),
                ('model', models.CharField(max_length=250)),
                ('description', models.CharField(blank=True, max_length=250)),
                ('unique_id', models.CharField(default=main.models.generate_unique_id, editable=False, max_length=5, unique=True)),
                ('supplier', models.CharField(blank=True, max_length=250)),
                ('price', models.IntegerField(default=0)),
                ('quantity', models.IntegerField()),
                ('quantity_warning', models.IntegerField(default=20)),
                ('quantity_alert', models.IntegerField(default=10)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('consumable', models.BooleanField(default=True)),
                ('self_pickup', models.BooleanField(default=False)),
                ('unique_component', models.BooleanField(default=False)),
                ('last_sn', models.CharField(blank=True, max_length=100)),
            ],
        ),
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
            name='PO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po_number', models.CharField(blank=True, max_length=250)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_area_name', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(max_length=255)),
                ('detail', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scrap_status', models.BooleanField(default=False)),
                ('scrap_list', models.TextField(blank=True, null=True)),
                ('purpose_type', models.TextField(choices=[('General', 'General'), ('New Project', 'New Project'), ('Exchange', 'Exchange')], default='General', max_length=255)),
                ('purpose_detail', models.TextField()),
                ('status', models.CharField(choices=[('Requested', 'Requested'), ('Staff', 'Staff'), ('Manager', 'Manager'), ('Preparing', 'Preparing'), ('Success', 'Success'), ('PickUp', 'PickUp')], default='Requested', max_length=255)),
                ('rejected', models.BooleanField(default=False)),
                ('self_pickup', models.BooleanField(default=False)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('complete_date', models.DateTimeField(blank=True)),
                ('pickup_date', models.DateTimeField(blank=True)),
                ('requester_name_center', models.CharField(blank=True, max_length=150, null=True)),
                ('requester_emp_center', models.CharField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SerialNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=100, unique=True)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='serial_numbers', to='main.component')),
                ('po', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.po')),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.request')),
            ],
        ),
        migrations.CreateModel(
            name='RequestComponentRelation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.component')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.request')),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='components',
            field=models.ManyToManyField(through='main.RequestComponentRelation', to='main.Component'),
        ),
        migrations.AddField(
            model_name='request',
            name='prepare_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prepare_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='staff_approved',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_approved', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='supervisor_approved',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_approved', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='po',
            name='production_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.productionarea'),
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
            name='MachineType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('production_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.productionarea')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('production_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.productionarea')),
            ],
        ),
        migrations.CreateModel(
            name='HistoryTrading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requester', models.CharField(blank=True, max_length=100, null=True)),
                ('staff_approved', models.CharField(blank=True, max_length=100, null=True)),
                ('supervisor_approved', models.CharField(blank=True, max_length=100, null=True)),
                ('trader', models.CharField(max_length=100)),
                ('left_qty', models.IntegerField(default=0)),
                ('gr_qty', models.IntegerField(default=0)),
                ('gi_qty', models.IntegerField(default=0)),
                ('scrap_qty', models.IntegerField(default=0)),
                ('purpose_detail', models.TextField()),
                ('purpose_type', models.CharField(blank=True, max_length=100, null=True)),
                ('request_id', models.CharField(blank=True, max_length=200)),
                ('serial_numbers', models.TextField(default='')),
                ('scrap_serial_numbers', models.TextField(default='')),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.component')),
                ('po_number', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.po')),
            ],
        ),
        migrations.AddField(
            model_name='component',
            name='component_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.componenttype'),
        ),
        migrations.AddField(
            model_name='component',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.department'),
        ),
        migrations.AddField(
            model_name='component',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.location'),
        ),
        migrations.AddField(
            model_name='component',
            name='machine_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.machinetype'),
        ),
        migrations.AddField(
            model_name='component',
            name='production_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.productionarea'),
        ),
        migrations.CreateModel(
            name='ApprovedRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production_area', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.productionarea')),
                ('staff_route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_route', to=settings.AUTH_USER_MODEL)),
                ('staff_route_second', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_route_second', to=settings.AUTH_USER_MODEL)),
                ('supervisor_route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_route', to=settings.AUTH_USER_MODEL)),
                ('supervisor_route_second', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_route_second', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='production_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.productionarea'),
        ),
        migrations.AddField(
            model_name='member',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
