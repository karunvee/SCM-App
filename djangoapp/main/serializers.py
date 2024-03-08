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
        fields = ['id', 'name', 'model', 'description', 'machine_type',
                  'component_type', 'department', 'location', 'issue_date',
                  'quantity', 'quantity_warning', 'quantity_alert', 
                  'consumable', 'image', 'serial_numbers']


class ComponentInfoSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    class Meta(object):
        model = Component
        fields = '__all__'
        
class SerialNumberWithComponentSerializer(serializers.ModelSerializer):
    component = ComponentInfoSerializer()
    class Meta(object):
        model = SerialNumber
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
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

class CartOrderSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField()
    class Meta(object):
        model = CartOrder
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    requester = serializers.StringRelatedField()
    # staff_approved = serializers.StringRelatedField()
    # supervisor_approved = serializers.StringRelatedField()
    class Meta(object):
        model = CartOrder
        fields = '__all__'
# Params
class EmployeeIdQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()

class ComponentQuerySerializer(serializers.Serializer):
    component_id = serializers.CharField()