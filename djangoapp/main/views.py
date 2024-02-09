from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

import time

@api_view(['GET'])
def component_list(request):
    component_list = Component.objects.all()
    serializers = ComponentSerializer(instance=component_list, many=True)
    context = {
        'component_list': serializers.data
    }
    time.sleep(1)
    return Response(context)

@api_view(['GET'])
def basic_info(request):
    ct_serializers = ComponentTypeSerializer(instance=ComponentType.objects.all(), many=True)
    d_serializers = DepartmentSerializer(instance=Department.objects.all(), many=True)
    l_serializers = LocationSerializer(instance=Location.objects.all(), many=True)
    context = {
        'component_type_list': ct_serializers.data,
        'department_list': d_serializers.data,
        'location_list': l_serializers.data
    }
    return Response(context)

@api_view(['POST', 'PUT'])
def add_component(request):
    try:
        image = request.data['image']
        name = request.data['name']
        model = request.data['model']
        sn = request.data['sn'].split(',')
        description = request.data['description']
        component_type, ct_created = ComponentType.objects.get_or_create(name = request.data['component_type'], defaults={})
        department, d_created = Department.objects.get_or_create(name = request.data['department'], defaults={})
        location, l_created = Location.objects.get_or_create(name = request.data['location'], defaults={})
        quantity = request.data['quantity']
        quantity_warning = request.data['quantity_warning']
        quantity_alert = request.data['quantity_alert']

        if not Component.objects.filter(name = name, model = model, department__name = request.data['department']).exists() or request.method == 'PUT':
            component_obj, c_created = Component.objects.update_or_create(
                name = name,
                model = model,
                defaults={
                    'image' : image,
                    'name' : name,
                    'model' : model,
                    'sn' : sn,
                    'description' : description,
                    'component_type' : component_type,
                    'department' : department,
                    'location' : location,
                    'quantity' : quantity,
                    'quantity_warning' : quantity_warning,
                    'quantity_alert' : quantity_alert,
                }
            )
            component_obj.save()

            return Response({"detail": "Successfully, %s was uploaded" % name}, status=status.HTTP_201_CREATED)
        else: 
            return Response({"detail": "Failure, duplicate data"}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"detail": "Failure, data as your provided is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def delete_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        component = component_obj.get()
        component.delete()
        return Response({"detail": "%s was deleted." % component.name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)
