from rest_framework import serializers
from .models import *

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Department
        fields = ['name']

class ComponentTypeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ComponentType
        fields = ['name']

class LocationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Location
        fields = ['pk', 'name']

class MachineTypeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MachineType
        fields = ['pk', 'name']

class PoSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PO
        fields = '__all__'

class SerialNumberSerializer(serializers.ModelSerializer):
    component = serializers.StringRelatedField()
    po = serializers.StringRelatedField()
    class Meta(object):
        model = SerialNumber
        fields = '__all__'

class ComponentSerializer(serializers.ModelSerializer):
    serial_numbers  = SerialNumberSerializer(many=True, read_only=True)
    department = serializers.StringRelatedField()
    machine_type = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    class Meta(object):
        model = Component
        fields = ['id', 'name', 'model', 'description', 'machine_type', 'unique_id', 'price',
                  'component_type', 'department', 'location', 'issue_date',
                  'quantity', 'quantity_warning', 'quantity_alert', 
                  'consumable', 'image', 'serial_numbers']

class ComponentWithoutSerialsSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    machine_type = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    class Meta(object):
        model = Component
        fields = ['id', 'name', 'model', 'description', 'machine_type', 'unique_id', 'price',
                  'component_type', 'department', 'location', 'issue_date',
                  'quantity', 'quantity_warning', 'quantity_alert', 
                  'consumable', 'image']

class ComponentInfoSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    machine_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    class Meta(object):
        model = Component
        fields = '__all__'

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
    # components = ComponentWithoutSerialsSerializer(many=True, read_only=True)
    class Meta(object):
        model = Request
        fields = ['id', 'requester', 'staff_approved', 'supervisor_approved', 'prepare_by','status', 
                  'rejected', 'purpose_detail', 'purpose_type', 'scrap_status', 'scrap_list',
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

class ProductionAreaSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProductionArea
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    production_area = ProductionAreaSerializer()
    class Meta(object):
        model = Member
        fields = '__all__'

class HistoryTradingSerializer(serializers.ModelSerializer):
    component = ComponentImageSerializer()
    po_number = PoSerializer()
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
    production_area = ProductionAreaSerializer()
    class Meta(object):
        model = ApprovedRoute
        fields = '__all__'

# Params
class ComponentFilterQuerySerializer(serializers.Serializer):
    component_type_content = serializers.CharField()
    machine_type_content = serializers.CharField()
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
    manager_id = serializers.CharField()

class GenerateSerialNumberQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()
    component_id = serializers.CharField()
    quantity = serializers.CharField()

class ProdAreaNameQuerySerializer(serializers.Serializer):
    production_area_name = serializers.CharField()
