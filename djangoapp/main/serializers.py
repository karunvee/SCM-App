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

class ComponentSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    component_type = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    class Meta(object):
        model = Component
        fields = '__all__'