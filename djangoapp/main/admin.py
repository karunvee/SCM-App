from django.contrib import admin
from .models import *
# Register your models here.
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name',
        'pk',
                    )
admin.site.register(Department, DepartmentAdmin)

class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name',
        'pk',
                    )
admin.site.register(Location, LocationAdmin)

class ComponentTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name',
        'pk',
                    )
admin.site.register(ComponentType, ComponentTypeAdmin)

class ComponentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'model', 'sn', 'supplier']
    list_display = (
        'name',
        'pk',
        'quantity',
        'model',
        'sn',
        'component_type',
        'location',
        'department'
                    )
    list_filter = ['component_type', 'department', 'location']
admin.site.register(Component, ComponentAdmin)