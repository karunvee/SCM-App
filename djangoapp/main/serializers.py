from rest_framework import serializers
from .models import *

class ProductionAreaSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProductionArea
        fields = '__all__'
        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Department
        fields = ['name']

class ComponentTypeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ComponentType
        fields = ['id', 'name']

class LocationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Location
        fields = ['id', 'name', 'for_tooling', 'last_inventory_date']



class PoSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PO
        fields = '__all__'

class LineSerializer(serializers.ModelSerializer):
    production_area = ProductionAreaSerializer()
    class Meta(object):
        model = Line
        fields = '__all__'

class SerialNumberSerializer(serializers.ModelSerializer):
    component = serializers.StringRelatedField()
    po = serializers.StringRelatedField()
    class Meta(object):
        model = SerialNumber
        fields = '__all__'

class MachineSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Machine
        fields = '__all__'
        

class MachineRelationSerializer(serializers.ModelSerializer):
    machine = MachineSerializer()
    line = serializers.StringRelatedField()
    class Meta(object):
        model = MachineRelation
        fields = '__all__'

class MachineWithShortageSerializer(serializers.ModelSerializer):
    total_machines = serializers.IntegerField()
    shortage_percent = serializers.FloatField()
    shortage_components = serializers.IntegerField()
    total_components = serializers.IntegerField()
    line = serializers.StringRelatedField()

    class Meta:
        model = Machine
        fields = ['id', 'name', 'image', 'type', 'line', 'total_machines', 'shortage_percent', 'shortage_components', 'total_components']

class ComponentOnlyInfoSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    modify_member = serializers.StringRelatedField()
    added_member = serializers.StringRelatedField()

    class Meta:
        model = Component
        fields = [
            'id', 'name', 'model', 'description', 'unique_id', 'price', 'supplier', 'mro_pn', 'consumable', 'image',
            'component_type', 'department', 'location', 'issue_date', 'self_pickup', 'unique_component',
            'quantity', 'quantity_warning', 'quantity_alert', 'last_inventory_date', 'next_inventory_date', 'price',
            'modify_member', 'added_member'
        ]

class ComponentSerializer(serializers.ModelSerializer):
    serial_numbers  = SerialNumberSerializer(many=True, read_only=True)
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    modify_member = serializers.StringRelatedField()
    added_member = serializers.StringRelatedField()

    # equipment_type = EquipmentTypeRelationSerializer(many=True, source='equipmenttyperelation_set')
    # machine_type = MachineTypeRelationSerializer(many=True, source='machinetyperelation_set')
    machine = MachineRelationSerializer(many=True, source='machinerelation_set')

    class Meta:
        model = Component
        fields = [
            'id', 'name', 'model', 'description', 'unique_id', 'price', 'supplier', 'mro_pn', 'consumable', 'image',
            'component_type', 'department', 'location', 'issue_date', 'self_pickup', 'unique_component',
            'quantity', 'quantity_warning', 'quantity_alert', 'last_inventory_date', 'next_inventory_date', 'serial_numbers', 
            # 'equipment_type', 'machine_type', 
            'machine',
            'modify_member', 'added_member'
        ]

class ComponentWithoutSerialsSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()

    # equipment_type = EquipmentTypeRelationSerializer(many=True, source='equipmenttyperelation_set')
    # machine_type = MachineTypeRelationSerializer(many=True, source='machinetyperelation_set')
    machine = MachineRelationSerializer(many=True, source='machinerelation_set')

    class Meta:
        model = Component
        fields = [
            'id', 'name', 'model', 'description', 'unique_id', 'price', 'supplier', 'mro_pn', 'consumable', 'image',
            'component_type', 'department', 'location', 'issue_date', 'self_pickup', 'unique_component',
            'quantity', 'quantity_warning', 'quantity_alert', 'last_inventory_date', 'next_inventory_date', 'missing_list',
            # 'equipment_type', 'machine_type'
            'machine'
        ]

class ComponentInfoSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()

    # equipment_type = EquipmentTypeRelationSerializer(many=True, source='equipmenttyperelation_set')
    # machine_type = MachineTypeRelationSerializer(many=True, source='machinetyperelation_set')

    Machine = MachineRelationSerializer(many=True, source='machinerelation_set')
    class Meta(object):
        model = Component
        fields = '__all__'

class PriorityComponentSerializer(serializers.ModelSerializer):
    machine_count = serializers.IntegerField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Component
        fields = ['id', 'name', 'model', 'quantity', 'quantity_alert', 'machine_count', 'image_url']

    def get_image_url(self, obj):
        return obj.image_url

class ComponentImageSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Component
        fields = ['id', 'name', 'model', 'image']
        
class RequestComponentRelationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = RequestComponentRelation
        fields = ['id', 'component', 'qty']

class RequestSerializer(serializers.ModelSerializer):
    requester = serializers.StringRelatedField()
    staff_approved = serializers.StringRelatedField()
    supervisor_approved = serializers.StringRelatedField()
    prepare_by = serializers.StringRelatedField()
    lines = LineSerializer(many=True)
    # components = ComponentWithoutSerialsSerializer(many=True, read_only=True)
    class Meta(object):
        model = Request
        fields = ['id', 'requester', 'staff_approved', 'supervisor_approved', 'prepare_by','status', 'pickup_status', 'lines',
                  'rejected', 'purpose_detail', 'purpose_type', 'scrap_status', 'scrap_list', 'self_pickup',
                  'requester_name_center', 'requester_emp_center',
                  'issue_date', 'complete_date']

class SerialNumberOnlySnSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = SerialNumber
        fields = ['serial_number']

class SerialNumberSerializer(serializers.ModelSerializer):
    po = PoSerializer()
    class Meta(object):
        model = SerialNumber
        fields = ['serial_number', 'po', 'issue_date']

class SerialNumberWithStrPoSerializer(serializers.ModelSerializer):
    po = serializers.StringRelatedField()
    class Meta(object):
        model = SerialNumber
        fields = ['serial_number', 'po', 'issue_date']

class SerialNumberWithComponentSerializer(serializers.ModelSerializer):
    component = ComponentInfoSerializer()
    class Meta(object):
        model = SerialNumber
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    production_area = ProductionAreaSerializer()
    class Meta(object):
        model = Member
        fields = '__all__'

class HistoryTradingSerializer(serializers.ModelSerializer):
    component = ComponentImageSerializer()
    po_number = PoSerializer()
    lines = LineSerializer(many=True)
    class Meta(object):
        model = HistoryTrading
        fields = '__all__'

class PoSerializer(serializers.ModelSerializer):
    production_area = serializers.StringRelatedField()
    class Meta(object):
        model = PO
        fields = '__all__'

class OrderTackingSerializer(serializers.ModelSerializer):
    po = serializers.StringRelatedField()
    class Meta(object):
        model = OrderTacking
        fields = '__all__'

class ApprovedRouteSerializer(serializers.ModelSerializer):
    staff_route = MemberSerializer()
    staff_route_second = MemberSerializer()
    supervisor_route = MemberSerializer()
    supervisor_route_second = MemberSerializer()
    approve_route = MemberSerializer()
    production_area = ProductionAreaSerializer()
    class Meta(object):
        model = ApprovedRoute
        fields = '__all__'

class InventoryReportSerializer(serializers.ModelSerializer):
    staff = MemberSerializer()
    location = LocationSerializer()
    class Meta(object):
        model = InventoryReport
        fields = '__all__'

class BorrowerRelationSerializer(serializers.ModelSerializer):
    component = ComponentWithoutSerialsSerializer(many=True)
    borrower = MemberSerializer(many=True)
    class Meta(object):
        model = BorrowerRelation
        fields = '__all__'

class ToolingSerializer(serializers.ModelSerializer):
    component = ComponentWithoutSerialsSerializer()
    location = LocationSerializer()
    borrower = MemberSerializer(many=True)
    class Meta(object):
        model = Tooling
        fields = '__all__'

class HistoryToolTradingSerializer(serializers.ModelSerializer):
    tooling = ToolingSerializer()
    class Meta(object):
        model = HistoryToolTrading
        fields = '__all__'

class ShiftDutySerializer(serializers.ModelSerializer):
    production_area = ProductionArea()
    member = MemberSerializer()
    class Meta(object):
        model = ShiftDuty
        fields = '__all__'

# Params
class ComponentProdNameTypeQuerySerializer(serializers.Serializer):
    production_name = serializers.CharField()
    type = serializers.CharField()

class ComponentProdNameQuerySerializer(serializers.Serializer):
    production_name = serializers.CharField()

class ComponentFilterQuerySerializer(serializers.Serializer):
    component_type_content = serializers.CharField()
    production_name = serializers.CharField()

class EmployeeIdQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()

class ComponentQuerySerializer(serializers.Serializer):
    component_id = serializers.CharField()

class RequestEmployeeIdQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()

class RequestQuerySerializer(serializers.Serializer):
    request_id = serializers.CharField()

class ApprovedRouteIdQuerySerializer(serializers.Serializer):
    route_id = serializers.CharField()

class ApprovedRouteIdUpdateQuerySerializer(serializers.Serializer):
    route_id = serializers.CharField()
    staff_id = serializers.CharField()
    supervisor_id = serializers.CharField()
    manager_id = serializers.CharField()

class GenerateSerialNumberQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()
    component_id = serializers.CharField()
    quantity = serializers.CharField()

class ProdAreaNameQuerySerializer(serializers.Serializer):
    production_area_name = serializers.CharField()

class ProdAreaNamePaginatorQuerySerializer(serializers.Serializer):
    date_start = serializers.CharField()
    date_end = serializers.CharField()
    search = serializers.CharField()
    production_area_name = serializers.CharField()
    # page_number = serializers.IntegerField()
    # qty_per_page = serializers.IntegerField()

class ApproveByMailQuerySerializer(serializers.Serializer):
    request_id = serializers.CharField()
    emp_id = serializers.CharField()


class EmployeeIdWithLocationQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()
    location = serializers.CharField()


class ProAreaWithLocationQuerySerializer(serializers.Serializer):
    production_name = serializers.CharField()
    location = serializers.CharField()

class LocationQuerySerializer(serializers.Serializer):
    location = serializers.CharField()
