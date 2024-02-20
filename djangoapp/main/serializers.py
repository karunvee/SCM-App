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

class SerialNumberSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = SerialNumber
        fields = ['id', 'serial_number']

class ComponentSerializer(serializers.ModelSerializer):
    serial_numbers  = SerialNumberSerializer(many=True, read_only=True)
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    class Meta(object):
        model = Component
        fields = ['id', 'name', 'model', 'description', 
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

class LoginQuerySerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    ad_server = serializers.CharField()

class CheckInQuerySerializer(serializers.Serializer):
    emp_id = serializers.CharField()
