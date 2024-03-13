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
        fields = ['name']

class MachineTypeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MachineType
        fields = ['name']

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
        fields = ['id', 'name', 'model', 'description', 'machine_type', 'purpose_detail', 'price',
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
        fields = ['id', 'name', 'model', 'description', 'machine_type', 'purpose_detail', 'price',
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

        
class RequestComponentRelationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = RequestComponentRelation
        fields = ['id', 'component', 'qty']

class RequestSerializer(serializers.ModelSerializer):
    requester = serializers.StringRelatedField()
    staff_approved = serializers.StringRelatedField()
    supervisor_approved = serializers.StringRelatedField()
    # components = ComponentWithoutSerialsSerializer(many=True, read_only=True)
    class Meta(object):
        model = Request
        fields = ['id', 'requester', 'staff_approved', 'supervisor_approved', 'status',
                  'issue_date', 'complete_date']

        
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
    member = serializers.StringRelatedField()
    component = ComponentInfoSerializer()
    class Meta(object):
        model = HistoryTrading
        fields = '__all__'

class OrderTackingSerializer(serializers.ModelSerializer):
    po = serializers.StringRelatedField()
    class Meta(object):
        model = OrderTacking
        fields = '__all__'

# Params
class ComponentFilterQuerySerializer(serializers.Serializer):
    component_type_content = serializers.CharField()
    machine_type_content = serializers.CharField()

class EmployeeIdQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()

class ComponentQuerySerializer(serializers.Serializer):
    component_id = serializers.CharField()

class RequestQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()