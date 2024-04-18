from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
import uuid

# Create your models here.
    
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
    prod_area_name = models.CharField(max_length = 255, unique=True)
    description = models.CharField(max_length = 255)
    detail = models.CharField(max_length = 3)

    def __str__(self):
        return self.prod_area_name

class Member(AbstractBaseUser, PermissionsMixin):
    emp_id = models.CharField(unique=True, max_length = 10)
    username = models.CharField(unique=True,max_length = 100)
    name = models.CharField(max_length = 200)
    department = models.CharField(max_length = 250)
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)

    email = models.EmailField(unique=True)

    is_user = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_center = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'  # Use name for authentication
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return "%s,%s" % (self.emp_id, self.name)

class ApprovedRoute(models.Model):
    staff_route = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='staff_route')
    staff_route_second  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='staff_route_second',blank=True, null=True)
    supervisor_route = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='supervisor_route')
    supervisor_route_second  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='supervisor_route_second',blank=True, null=True)
    production_area = models.OneToOneField(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.production_area.prod_area_name

class Department(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name
    
class Location(models.Model):
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name
    
class ComponentType(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name

class MachineType(models.Model):
    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name

class Component(models.Model):
    image = models.ImageField(upload_to='images/', blank=True)
    name = models.CharField(max_length = 250)
    model = models.CharField(max_length = 250)
    description = models.CharField(max_length = 250, blank = True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    machine_type = models.ForeignKey(MachineType, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length = 3, blank = False) 
    
    supplier = models.CharField(max_length = 250, blank = True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    price = models.IntegerField(default=0)
    quantity = models.IntegerField()
    quantity_warning = models.IntegerField(default=20)
    quantity_alert = models.IntegerField(default=10)
    issue_date = models.DateTimeField(auto_now_add=True)
    consumable = models.BooleanField(default= True)

    production_area = models.ForeignKey(ProductionArea, on_delete=models.CASCADE)
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''
        
    def __str__(self):
        return "%s, %s" % (self.name, self.model)

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
    
    scrap_status = models.BooleanField(default=True)
    scrap_list = models.TextField(blank = True, null=True)

    purpose_type = models.TextField(max_length = 255, choices=PURPOSE_TYPE, default=PURPOSE_TYPE[0][0])
    purpose_detail = models.TextField()
    prepare_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='prepare_by', blank=True, null=True)

    status =  models.CharField(max_length = 255, choices=STATUS, default=STATUS[0][0])
    rejected = models.BooleanField(default= False)
    # self_pick = models.BooleanField(default= False)
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
    purpose_detail = models.TextField()
    purpose_type = models.CharField(max_length = 100, blank=True, null=True)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)

    request_id = models.CharField(max_length = 200, blank=True)
    po_number = models.ForeignKey(PO, on_delete=models.SET_NULL, blank=True, null=True)

    serial_numbers = models.TextField(default='')
    scrap_serial_numbers = models.TextField(default='')

    issue_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.requester