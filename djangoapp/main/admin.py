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

class SerialNumberAdmin(admin.ModelAdmin):
    search_fields = ['serial_number']
    list_display = (
        'serial_number',
        'component',
        'pk',
                    )
admin.site.register(SerialNumber, SerialNumberAdmin)

class SerialNumberInline(admin.TabularInline):  # Use 'StackedInline' for a different layout
    model = SerialNumber
    extra = 1 
class ComponentAdmin(admin.ModelAdmin):
    inlines = [SerialNumberInline]
    search_fields = ['name', 'model', 'supplier']
    list_display = (
        'name',
        'pk',
        'quantity',
        'model',
        'get_serial_numbers',
        'component_type',
        'location',
        'department'
                    )
    list_filter = ['component_type', 'department', 'location']

    def get_serial_numbers(self, obj):
        return ', '.join([sn.serial_number for sn in obj.serial_numbers.all()])
    
    get_serial_numbers.short_description = 'Serial Numbers'
admin.site.register(Component, ComponentAdmin)

class MemberAdmin(admin.ModelAdmin):
    search_fields = ['emp_id', 'username']
    list_filter = ['department', 'is_staff', 'is_user']

    list_display = (
        'username',
        'emp_id',
        'pk',
        'name',
        'email',
        'department',
        'is_staff',
        'is_user',
        'is_superuser',
        'date_joined'
                    )
    
    fieldsets = (
        (None, {'fields': ('username', 'date_joined')}),
        ('Permission', {'fields': ( 'is_staff', 'is_user', 'is_superuser')}),
        ('Personal', {'fields': ( 'name', 'emp_id', 'email', )})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'emp_id', 'email', 'department',
                       'is_staff', 'is_user', 'is_superuser', 'password1', 'password2')
        }),
    )
    
admin.site.register(Member, MemberAdmin)


class HistoryTradingAdmin(admin.ModelAdmin):
    search_fields = ['member__username', 'member__emp_id', 'component__name', 'component__model']
    list_display = (
        'member',
        'pk',
        'component',
        'serial_numbers',
        'issue_date'
                    )
    list_filter = ['component__component_type', 'component__department']
    
admin.site.register(HistoryTrading, HistoryTradingAdmin)