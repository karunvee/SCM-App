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
    
class Member(AbstractBaseUser, PermissionsMixin):
    emp_id = models.CharField(unique=True, max_length = 10)
    username = models.CharField(unique=True,max_length = 100)
    name = models.CharField(max_length = 200)
    department = models.CharField(max_length = 250)
    email = models.EmailField(unique=True)

    is_user = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'  # Use name for authentication
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return "%s,%s" % (self.emp_id, self.name)
    
class Department(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name
    
class ComponentType(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name

class MachineType(models.Model):
    name = models.CharField(max_length = 250)
    def __str__(self):
        return self.name

class Component(models.Model):
    image = models.ImageField(upload_to='images/', blank=True)
    name = models.CharField(max_length = 250)
    model = models.CharField(max_length = 250)
    # sn = ArrayField(models.CharField(max_length=50), blank=True)
    # sn_list = models.ManyToManyField(SerialNumber) 
    description = models.CharField(max_length = 250, blank = True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    machine_type = models.ForeignKey(MachineType, on_delete=models.CASCADE)
    supplier = models.CharField(max_length = 250, blank = True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    quantity_warning = models.IntegerField(default=20)
    quantity_alert = models.IntegerField(default=10)
    issue_date = models.DateTimeField(auto_now_add=True)
    consumable = models.BooleanField(default= True)

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

    def __str__(self):
        return self.po_number 


class SerialNumber(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='serial_numbers')
    po = models.ForeignKey(PO, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.serial_number 
    

class HistoryTrading(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    serial_numbers = models.TextField()
    issue_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member.name 

class WatchList(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    serial_number = models.ForeignKey(SerialNumber, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    warning_period = models.IntegerField(default = 7)
    alert_period = models.IntegerField(default = 14)

    def __str__(self):
        return self.serial_number.serial_number 

    
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
    
class RequestComponentRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey('Request', on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

class Request(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='requester')

    staff_approved = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='staff_approved')
    supervisor_approved = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='supervisor_approved')

    components = models.ManyToManyField(Component, through='RequestComponentRelation')
    order_ready = models.BooleanField(default=False)
    issue_date = models.DateTimeField(auto_now_add=True)
    complete_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id}"