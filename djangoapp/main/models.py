from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
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

class Component(models.Model):
    image = models.ImageField(upload_to='images/', blank=True)
    name = models.CharField(max_length = 250)
    model = models.CharField(max_length = 250)
    sn = ArrayField(models.CharField(max_length=50), blank=True)
    description = models.CharField(max_length = 250, blank = True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    supplier = models.CharField(max_length = 250, blank = True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    quantity_warning = models.IntegerField(default=20)
    quantity_alert = models.IntegerField(default=10)
    issue_date = models.DateTimeField(auto_now_add=True)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''
        
    def __str__(self):
        return "%s, %s" % (self.name, self.model)
    
class Post(models.Model):
    name = models.CharField(max_length=200)
    tags = ArrayField(models.CharField(max_length=200), blank=True)

    def __str__(self):
        return self.name