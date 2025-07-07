from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
import uuid
import random
import string
import os
from datetime import datetime, timedelta

# Create your models here.
def generate_unique_id():
    length = 5
    characters = string.ascii_uppercase + string.digits
    unique_id = ''.join(random.choices(characters, k=length))
    # Check if this ID is already in use
    while Component.objects.filter(unique_id=unique_id).exists():
        unique_id = ''.join(random.choices(characters, k=length))
    return unique_id

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.is_user = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class ProductionArea(models.Model):
    prod_area_name = models.CharField(max_length = 100, unique=True)
    mes_factory = models.CharField(max_length = 100, blank=True, null=True)
    description = models.CharField(max_length = 255)
    detail = models.CharField(max_length = 3)

    def __str__(self):
        return self.prod_area_name

class Line(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    line_name = models.CharField(unique=True, max_length = 10)
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):

        return self.line_name

class CostCenter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length = 255, unique=True)
    cost_center_number = models.CharField(max_length = 255, unique=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f'{self.name}, {self.cost_center_number}'
    
class Member(AbstractBaseUser, PermissionsMixin):
    image = models.ImageField(upload_to='person_picture/', blank=True)

    emp_id = models.CharField(unique=True, max_length = 10)
    username = models.CharField(unique=True,max_length = 100)
    name = models.CharField(max_length = 200)
    department = models.CharField(max_length = 250, blank=True, null=True)
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.CASCADE, blank=True, null=True)

    email = models.EmailField(unique=True, blank=True, null=True)
    tel = models.CharField(max_length = 12, blank=True, null=True)
    line_id = models.CharField(max_length = 20, blank=True, null=True)

    is_administrator = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_center = models.BooleanField(default=False)
    is_local = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    ROLES = (('NONE', 'NONE'), ('User', 'User'), ('Fixture Staff', 'Fixture Staff'), ('Spare Part Staff', 'Spare Part Staff'), ('Modify Part Staff', 'Modify Part Staff'), ('Management Staff', 'Management Staff'), ('-', '-'))
    member_role = models.CharField(max_length = 255, choices=ROLES, default=ROLES[0][0])

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'  # Use name for authentication
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        try:
            # Check if the instance already exists in the database
            existing = Member.objects.get(id=self.id)
            if existing.image and self.image and existing.image != self.image:
                # Delete the old image file
                if os.path.isfile(existing.image.path):
                    os.remove(existing.image.path)
        except Member.DoesNotExist:
            # New object, no action needed
            pass

        super(Member, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(Member, self).delete(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def __str__(self):
        return "%s,%s" % (self.emp_id, self.name)

class ApprovedRoute(models.Model):
    production_area = models.OneToOneField(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)

    staff_route = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='staff_route')
    staff_route_second  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='staff_route_second',blank=True, null=True)
    supervisor_route = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='supervisor_route')
    supervisor_route_second  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='supervisor_route_second',blank=True, null=True)

    approve_route = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='approve_route',blank=True, null=True)

    def __str__(self):
        return self.production_area.prod_area_name
    
class CarbonCopyRoute(models.Model):
    approve_route = models.ForeignKey(ApprovedRoute, on_delete=models.CASCADE, related_name='carbon_copy_route')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='cc_member')

    def __str__(self):
        return f'{self.member.name}, {self.approve_route.production_area.prod_area_name}'


class Department(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name
    
class Location(models.Model):
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length = 250)
    for_tooling = models.BooleanField(default=False)
    last_inventory_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name
    
class ComponentType(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name

class Machine(models.Model):
    TYPES = (('DSM', 'DSM'), ('OFFLINE', 'OFFLINE'))
    type =  models.CharField(max_length = 255, choices=TYPES, default=TYPES[0][0])
    
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length = 250)

    image = models.ImageField(upload_to='images/machines/', blank=True)
    def save(self, *args, **kwargs):
        try:
            # Check if the instance already exists in the database
            existing = Machine.objects.get(id=self.id)
            if existing.image and self.image and existing.image != self.image:
                # Delete the old image file
                if os.path.isfile(existing.image.path):
                    os.remove(existing.image.path)
        except Machine.DoesNotExist:
            # New object, no action needed
            pass

        super(Machine, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(Machine, self).delete(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'production_area'], name='unique_machine_per_area')
        ]

    def __str__(self):
        return self.name

class MachineType(models.Model):
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length = 250)

    image = models.ImageField(upload_to='images/machines/', blank=True)
    def save(self, *args, **kwargs):
        try:
            # Check if the instance already exists in the database
            existing = MachineType.objects.get(id=self.id)
            if existing.image and self.image and existing.image != self.image:
                # Delete the old image file
                if os.path.isfile(existing.image.path):
                    os.remove(existing.image.path)
        except MachineType.DoesNotExist:
            # New object, no action needed
            pass

        super(MachineType, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(MachineType, self).delete(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'production_area'], name='unique_machine_type_per_area')
        ]

    def __str__(self):
        return self.name
    
class EquipmentType(models.Model):
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length = 250)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'production_area'], name='unique_equipment_type_per_area')
        ]

    def __str__(self):
        return self.name

class Component(models.Model):
    image = models.ImageField(upload_to='images/', blank=True)
    name = models.CharField(max_length = 250)
    model = models.CharField(max_length = 250)
    description = models.CharField(max_length = 250, blank = True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    # machine_type = models.ForeignKey(MachineType, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=5, unique=True, default=generate_unique_id, editable=False)
    
    supplier = models.CharField(max_length = 250, blank = True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    price = models.IntegerField(default=0)
    quantity = models.IntegerField()
    quantity_warning = models.IntegerField(default=20)
    quantity_alert = models.IntegerField(default=10)
    issue_date = models.DateTimeField(auto_now_add=True)
    consumable = models.BooleanField(default= True)
    self_pickup = models.BooleanField(default= False)
    unique_component = models.BooleanField(default= False)

    last_sn = models.CharField(max_length = 100, blank = True)
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE)

    last_inventory_date = models.DateTimeField(default=timezone.now)
    next_inventory_date = models.DateTimeField(default=timezone.now)
    missing_list = models.TextField(blank = True, null=True) 

    mro_pn =  models.CharField(max_length = 12, blank=True)

    modify_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='modify_c_member')
    added_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='added_c_member')

    machine = models.ManyToManyField(Machine, through='MachineRelation')
    # equipment_type = models.ManyToManyField(EquipmentType, through='EquipmentTypeRelation')
    # machine_type = models.ManyToManyField(MachineType, through='MachineTypeRelation')

    def save(self, *args, **kwargs):
        try:
            # Check if the instance already exists in the database
            existing = Component.objects.get(id=self.id)
            if existing.image and self.image and existing.image != self.image:
                # Delete the old image file
                if os.path.isfile(existing.image.path):
                    os.remove(existing.image.path)
        except Component.DoesNotExist:
            # New object, no action needed
            pass

        super(Component, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(Component, self).delete(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''
        
    def __str__(self):
        return f"{self.name}, {self.model}"


class MachineRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    m_quantity = models.PositiveIntegerField(default=1)
    factor = models.FloatField(default=1)
    modify_date = models.DateTimeField(default=timezone.now)
    added_date = models.DateTimeField(auto_now_add=True)

    line = models.ForeignKey(Line, on_delete=models.CASCADE, blank=True, null=True)

    modify_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='modify_ms_member')
    added_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='added_ms_member')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['machine', 'line'], name='unique_machine_per_line')
        ]

    def __str__(self):
        return f"{self.machine.name}, {self.component.name}"


# DSM Machine
class EquipmentTypeRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    m_quantity = models.PositiveIntegerField(default=1)
    factor = models.FloatField(default=1)
    modify_date = models.DateTimeField(default=timezone.now)
    added_date = models.DateTimeField(auto_now_add=True)

    line = models.ForeignKey(Line, on_delete=models.CASCADE, blank=True, null=True)

    modify_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='modify_els_member')
    added_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='added_els_member')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['equipment_type', 'line'], name='unique_equipment_type_per_line')
        ]

    def __str__(self):
        return f"{self.equipment_type.name}, {self.component.name}"

# Offline Machine
class MachineTypeRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine_type = models.ForeignKey(MachineType, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    m_quantity = models.PositiveIntegerField(default=1)
    factor = models.FloatField(default=1)
    modify_date = models.DateTimeField(default=timezone.now)
    added_date = models.DateTimeField(auto_now_add=True)

    line = models.ForeignKey(Line, on_delete=models.CASCADE, blank=True, null=True)

    modify_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='modify_mls_member')
    added_member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True, related_name='added_mls_member')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['machine_type', 'line'], name='unique_machine_type_per_line')
        ]

    def __str__(self):
        return f"{self.machine_type.name}, {self.component.name}"

class Tooling(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity_amount = models.IntegerField()
    quantity_available = models.IntegerField()
    location = models.ForeignKey(Location,  on_delete=models.SET_NULL, blank=True, null=True)
    borrower = models.ManyToManyField(Member, through='BorrowerRelation')

    def __str__(self):
        return f"{self.component.name}, {self.component.quantity}"
    
class BorrowerRelation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    tooling = models.ForeignKey(Tooling, on_delete=models.CASCADE)
    permanent_borrowing = models.BooleanField(default= False)
    borrowed_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.name}, {self.tooling.component.name}, {self.borrowed_date}"

class PO(models.Model):
    po_number = models.CharField(max_length = 250, blank = True)
    issue_date = models.DateTimeField(auto_now_add=True)
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.po_number 

    
class OrderTacking(models.Model):
    STATUS = (('Processing', 'Processing'), ('PR', 'PR'), ('PO', 'PO'), ('Shipping', 'Shipping'), ('Good Received', 'Good Received'), ('In-House', 'In-House'))
    status =  models.CharField(max_length = 255, choices=STATUS, default=STATUS[0][0])
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po = models.ForeignKey(PO, on_delete=models.CASCADE, blank=True)
    pr_date = models.DateTimeField(default=timezone.now)
    po_date = models.DateTimeField(default=timezone.now)
    shipping_date = models.DateTimeField(default=timezone.now)
    receive_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id

class Request(models.Model):
    STATUS = (('Requested', 'Requested'), ('Staff', 'Staff'), ('Manager', 'Manager'), ('Preparing', 'Preparing'), ('Success', 'Success'), ('PickUp', 'PickUp'))
    PURPOSE_TYPE = (('General', 'General'), ('New Project', 'New Project'), ('Exchange', 'Exchange'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='requester')
    staff_approved = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='staff_approved')
    supervisor_approved = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='supervisor_approved')
    
    scrap_status = models.BooleanField(default=False)
    scrap_list = models.TextField(blank = True, null=True)

    lines = models.ManyToManyField(Line, related_name='lines_request')

    purpose_type = models.TextField(max_length = 255, choices=PURPOSE_TYPE, default=PURPOSE_TYPE[0][0])
    purpose_detail = models.TextField()
    prepare_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='prepare_by', blank=True, null=True)

    status =  models.CharField(max_length = 255, choices=STATUS, default=STATUS[0][0])
    pickup_status =  models.BooleanField(default= False)
    rejected = models.BooleanField(default= False)
    self_pickup = models.BooleanField(default= False)

    issue_date = models.DateTimeField(auto_now_add=True)
    complete_date = models.DateTimeField(blank = True)
    pickup_date = models.DateTimeField(blank = True)
    components = models.ManyToManyField(Component, through='RequestComponentRelation')

    requester_name_center = models.CharField(max_length = 150, blank = True, null=True)
    requester_emp_center = models.CharField(max_length = 8, blank = True, null=True)

    def update_status_to_next(self):
        current_status_index = [status[0] for status in self.STATUS].index(self.status)
        next_status_index = current_status_index + 1

        # Check if there's a next status available
        if next_status_index < len(self.STATUS):
            next_status = self.STATUS[next_status_index][0]
            self.status = next_status
            self.save()
            return True
        else:
            return False
    
    def get_status_index(self):
        for index, (status_code, _) in enumerate(self.STATUS):
            if status_code == self.status:
                return index
        # Return -1 if status is not found
        return -1

    def __str__(self):
        return f"{self.id}"
    
class RequestComponentRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.component.name}"
    
class SerialNumber(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='serial_numbers')
    po = models.ForeignKey(PO, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)

    request = models.ForeignKey(Request, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.serial_number 

class HistoryTrading(models.Model):
    requester = models.CharField(max_length = 100, blank=True, null=True)
    staff_approved = models.CharField(max_length = 100, blank=True, null=True)
    supervisor_approved = models.CharField(max_length = 100, blank=True, null=True)
    trader = models.CharField(max_length = 100)

    left_qty = models.IntegerField(default=0)
    gr_qty = models.IntegerField(default=0)
    gi_qty = models.IntegerField(default=0)
    scrap_qty = models.IntegerField(default=0)

    lines = models.ManyToManyField(Line, related_name='lines_history')

    purpose_detail = models.TextField()
    purpose_type = models.CharField(max_length = 100, blank=True, null=True)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)

    request_id = models.CharField(max_length = 200, blank=True)
    po_number = models.ForeignKey(PO, on_delete=models.SET_NULL, blank=True, null=True)

    serial_numbers = models.TextField(default='')
    scrap_serial_numbers = models.TextField(default='')

    issue_date = models.DateTimeField(auto_now_add=True)
    request_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.requester}, id: {self.pk}, {self.issue_date}"
    

class HistoryToolTrading(models.Model):
    MODE = (('Borrow', 'Borrow'), ('Return', 'Return'))

    topic = models.CharField(max_length = 255, choices=MODE, default=MODE[0][0])
    borrower = models.CharField(max_length = 100)
    trader = models.CharField(max_length = 100)

    tooling = models.ForeignKey(Tooling, on_delete=models.CASCADE)

    issue_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tooling}, {self.issue_date}"


class InventoryReport(models.Model):
    STATUS = (('Abnormal', 'Abnormal'), ('Normal', 'Normal'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    staff = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length = 255, choices=STATUS, default=STATUS[0][0])
    missing_list = models.TextField(blank = True, null=True)
    inventory_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location.name}, {self.status}"
    
def one_week_later():
    return timezone.now() + timedelta(days=7)

class ShiftDuty(models.Model):
    SHIFT = (('DAY', 'DAY'), ('NIGHT', 'NIGHT'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    shift = models.CharField(max_length = 255, choices=SHIFT, default=SHIFT[0][0])
    period_start = models.DateTimeField(default=timezone.now)
    period_end = models.DateTimeField(default=one_week_later)

    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.shift}, {self.member.name}"
