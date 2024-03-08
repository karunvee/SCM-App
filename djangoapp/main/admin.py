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

class MachineTypeAdmin(admin.ModelAdmin):
    search_fields = ['machine_name']
    list_display = (
        'name',
        'pk',
                    )
admin.site.register(MachineType, MachineTypeAdmin)

class POAdmin(admin.ModelAdmin):
    search_fields = ['po_number']
    list_display = (
        'po_number',
        'pk',
        'issue_date'
                    )
admin.site.register(PO, POAdmin)

class SerialNumberAdmin(admin.ModelAdmin):
    search_fields = ['serial_number', 'po__po_number']
    list_display = (
        'serial_number',
        'component',
        'po',
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
        'is_user',
        'is_staff',
        'is_supervisor',
        'is_superuser',
        'date_joined'
                    )
    fieldsets = (
        (None, {'fields': ('username', 'date_joined')}),
        ('Permission', {'fields': ( 'is_staff', 'is_user', 'is_supervisor', 'is_superuser')}),
        ('Personal', {'fields': ( 'name', 'emp_id', 'email', )})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'emp_id', 'email', 'department',
                       'is_staff', 'is_supervisor' , 'is_user', 'is_superuser', 'password1', 'password2')
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

class OrderTackingAdmin(admin.ModelAdmin):
    search_fields = ['po__po_number', 'order__id']
    list_display = (
        'pk',
        'status',
        'po',
        'pr_date',
        'po_date',
        'shipping_date',
        'receive_date'
                    )
    list_filter = ['status']
admin.site.register(OrderTacking, OrderTackingAdmin)

class CartOrderAdmin(admin.ModelAdmin):
    search_fields = ['member__username', 'member__name', 'member__emp_id']
    list_display = (
        'member',
        'pk',
        'serial_numbers',
                    )
    list_filter = ['member__department']
admin.site.register(CartOrder, CartOrderAdmin)

class RequestAdmin(admin.ModelAdmin):
    search_fields = ['id', 'requester__username', 'requester__name', 'requester__emp_id']
    list_display = (
        'id',
        'requester',
        'staff_approved',
        'supervisor_approved',
        'order_ready',
        'serial_numbers',
        'issue_date',
        'complete_date',
                    )
    list_filter = ['order_ready']
admin.site.register(Request, RequestAdmin)