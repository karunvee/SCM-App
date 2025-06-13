from django.contrib import admin
from .models import *
# Register your models here.

class CostCenterAdmin(admin.ModelAdmin):
    search_fields = ['name', 'cost_center_number']
    list_display = (
        'cost_center_number',
        'name',
        'id',
                    )
admin.site.register(CostCenter, CostCenterAdmin)

class ProductionAreaAdmin(admin.ModelAdmin):
    search_fields = ['id', 'prod_area_name']
    list_display = (
        'id',
        'prod_area_name',
        'description',
        'detail',
                    )
admin.site.register(ProductionArea, ProductionAreaAdmin)

class LineAdmin(admin.ModelAdmin):
    search_fields = ['id', 'line_name', 'production_area__prod_area_name']
    list_display = (
        'line_name',
        'id',
        'production_area',
        'added_date',
                    )
admin.site.register(Line, LineAdmin)

class EquipmentTypeRelationAdmin(admin.ModelAdmin):
    search_fields = ['id', 'equipment_type__name', 'component__name', 'component__model']
    list_display = (
        'id',
        'component',
        'safety_number',
        'equipment_type',
                    )
admin.site.register(EquipmentTypeRelation, EquipmentTypeRelationAdmin)

class MachineTypeRelationRelationAdmin(admin.ModelAdmin):
    search_fields = ['id', 'machine_type__name', 'component__name', 'component__model']
    list_display = (
        'id',
        'component',
        'safety_number',
        'machine_type',
                    )
admin.site.register(MachineTypeRelation, MachineTypeRelationRelationAdmin)

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
        'production_area',
        'for_tooling',
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
        'request',
        'po',
        'pk',
                    )
admin.site.register(SerialNumber, SerialNumberAdmin)

class SerialNumberInline(admin.TabularInline):  # Use 'StackedInline' for a different layout
    model = SerialNumber
    extra = 1 

class MachineTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name',
        'quantity',
        'production_area',
        'pk',
                    )
admin.site.register(MachineType, MachineTypeAdmin)

class MachineTypeRelationInline(admin.TabularInline):
    model = MachineTypeRelation
    extra = 1  # Number of empty forms to display
    fields = ('machine_type', 'safety_number', 'modify_date', 'added_date')
    readonly_fields = ('modify_date', 'added_date')  # Make these fields read-only

class EquipmentTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name',
        'quantity',
        'production_area',
        'pk',
                    )
admin.site.register(EquipmentType, EquipmentTypeAdmin)

class EquipmentTypeRelationInline(admin.TabularInline):
    model = EquipmentTypeRelation
    extra = 1  # Number of empty forms to display
    fields = ('equipment_type', 'safety_number', 'modify_date', 'added_date')
    readonly_fields = ('modify_date', 'added_date')  # Make these fields read-only

class ComponentAdmin(admin.ModelAdmin):
    inlines = [MachineTypeRelationInline, EquipmentTypeRelationInline, SerialNumberInline]
    search_fields = ['name', 'model', 'supplier']
    list_display = (
        'name',
        # 'unique_id',
        'pk',
        'quantity',
        'model',
        'self_pickup',
        'unique_component',
        'location',
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
        'production_area',
        'department',
        'is_local',
        'is_user',
        'is_staff',
        'is_supervisor',
        'is_superuser',
        'date_joined'
                    )
    fieldsets = (
        (None, {'fields': ('username', 'date_joined', 'production_area')}),
        ('Permission', {'fields': ( 'member_role', 'is_staff', 'is_user', 'is_supervisor', 'is_superuser', 'is_center', 'is_local', 'is_administrator')}),
        ('Detail', {'fields': ( 'name', 'emp_id', 'department', 'tel', 'line_id', 'email', 'image')})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'emp_id', 'email', 'department', 'production_area',
                       'is_staff', 'is_supervisor' , 'is_user', 'is_superuser', 'password1', 'password2')
        }),
    )
admin.site.register(Member, MemberAdmin)

class CarbonCopyRouteAdmin(admin.ModelAdmin):
    search_fields = ['member']
    list_display = (
        'pk',
        'approve_route',
        'member',
                    )
    list_filter = ['approve_route']
admin.site.register(CarbonCopyRoute, CarbonCopyRouteAdmin)

class CarbonCopyRouteInline(admin.TabularInline):  # Use 'StackedInline' for a different layout
    model = CarbonCopyRoute
    extra = 1 

class BorrowerRelationAdmin(admin.ModelAdmin):
    search_fields = ['tooling__component__name', "member__username", "member__name", "member__emp_id"]
    list_filter = ['permanent_borrowing']
    list_display = (
        'member',
        'tooling',
        'permanent_borrowing',
        'borrowed_date',
                    )
admin.site.register(BorrowerRelation, BorrowerRelationAdmin)


class BorrowerRelationInline(admin.TabularInline):
    model = BorrowerRelation
    extra = 1  # Number of empty forms to display
    fields = ('member', 'tooling')
    readonly_fields = ['borrowed_date']  # Make these fields read-only

class ToolingAdmin(admin.ModelAdmin):
    inlines = [BorrowerRelationInline]
    search_fields = ['component__name']
    list_display = (
        'component',
        'quantity_amount',
        'quantity_available',
                    )
admin.site.register(Tooling, ToolingAdmin)

class ApprovedRouteAdmin(admin.ModelAdmin):
    inlines = [CarbonCopyRouteInline]
    search_fields = ['id', 'supervisor_route__name']
    list_display = (
        'id',
        'staff_route',
        'supervisor_route',
        'production_area',
        'approve_route',
                    )
    def get_cc_members(self, obj):
        return ', '.join([cc_member.member.email for cc_member in obj.carbon_copy_route.all()])
    
    get_cc_members.short_description = 'CC Members'

admin.site.register(ApprovedRoute, ApprovedRouteAdmin)

class HistoryTradingAdmin(admin.ModelAdmin):
    search_fields = ['requester', 'component__name', 'component__model', 'request_id']
    list_display = (
        'issue_date',
        'request_id',
        'gr_qty', 'gi_qty', 'scrap_qty',
        'pk',
        'component',
        'serial_numbers',
        'requester'
                    )
    fieldsets = (
        (None, {'fields': ['requester']}),
        ('approved', {'fields': ( 'staff_approved', 'supervisor_approved', 'trader')}),
        ('quantity', {'fields': ( 'left_qty', 'gr_qty', 'gi_qty', 'scrap_qty')}),
        ('information', {'fields': ( 'purpose_detail', 'purpose_type', 'component', 'request_id', 'po_number', 'lines')}),
        ('items', {'fields': ( 'serial_numbers', 'scrap_serial_numbers')})
    )
    
    list_filter = ['component__component_type', 'component__department']
admin.site.register(HistoryTrading, HistoryTradingAdmin)


class HistoryToolTradingAdmin(admin.ModelAdmin):
    search_fields = ['trader', 'tooling__component__name', 'tooling__component__model']
    list_display = (
        'issue_date',
        'topic',
        'borrower', 'trader',
        'tooling',
                    )
    
    list_filter = ['tooling__component__component_type']
admin.site.register(HistoryToolTrading, HistoryToolTradingAdmin)

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

class RequestComponentRelationAdmin(admin.ModelAdmin):
    search_fields = ['id', 'request__requester__username', 'request__requester__name', 'request__requester__emp_id', 'component__name', 'component__model']
    list_display = (
        'id',
        'request',
        'component',
        'qty',
                    )
admin.site.register(RequestComponentRelation, RequestComponentRelationAdmin)



class RequestAdmin(admin.ModelAdmin):
    search_fields = ['id', 'requester__username', 'requester__name', 'requester__emp_id']
    list_display = (
        'id',
        'requester',
        'staff_approved',
        'supervisor_approved',
        'status',
        'rejected',
        'issue_date',
        'complete_date',
                    )
    list_filter = ['status']
admin.site.register(Request, RequestAdmin)


class InventoryReportAdmin(admin.ModelAdmin):
    search_fields = ['id', 'location__name', 'inventory_date']
    list_filter = ['status']

    list_display = (
        'id',
        'status',
        'location',
        'inventory_date'
                    )
    list_filter = ['status']
admin.site.register(InventoryReport, InventoryReportAdmin)


class ShiftDutyAdmin(admin.ModelAdmin):
    search_fields = ['id', 'production_area__prod_area_name','member__username', 'member__name', 'member__emp_id']

    list_display = (
        'id',
        'production_area',
        'member',
        'period_start',
        'period_end'
                    )
admin.site.register(ShiftDuty, ShiftDutyAdmin)