from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

import time
import ldap3

@api_view(['POST'])
def login_user(request, emp_id):
    try:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_user(request, emp_id):
    try:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



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


@api_view(['POST'])
def add_component(request):
    try:
        print(request.data)
        image = request.data.get('image')
        name = request.data.get('name')
        model = request.data.get('model')
        description = request.data.get('description')
        serial_numbers = request.data.get('serial_numbers').split(',')
        print(serial_numbers)
        component_type, ct_created = ComponentType.objects.get_or_create(name=request.data.get('component_type'), defaults={})
        department, d_created = Department.objects.get_or_create(name=request.data.get('department'), defaults={})
        location, l_created = Location.objects.get_or_create(name=request.data.get('location'), defaults={})
        quantity = request.data.get('quantity')
        quantity_warning = request.data.get('quantity_warning')
        quantity_alert = request.data.get('quantity_alert')

        if not Component.objects.filter(name=name, model=model, department__name=request.data.get('department')).exists():
            component_obj = Component.objects.create(
            image=image,
            name=name,
            model=model,
            description=description,
            component_type=component_type,
            department=department,
            location=location,
            quantity=quantity,
            quantity_warning=quantity_warning,
            quantity_alert=quantity_alert,
            )
            serial_container = []
            for sn in serial_numbers:
                serial_container.append(SerialNumber(serial_number=sn, component=component_obj))
            SerialNumber.objects.bulk_create(serial_container)

            serializer = ComponentSerializer(component_obj)
            return Response({"detail": f"Successfully added {name}.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Failure, duplicate data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        component_obj = component_obj.first()
        image = request.data['image']
        name = request.data['name']
        model = request.data['model']
        serial_numbers = request.data['serial_numbers'].split(',')
        description = request.data['description']
        component_type, ct_created = ComponentType.objects.get_or_create(name = request.data['component_type'], defaults={})
        department, d_created = Department.objects.get_or_create(name = request.data['department'], defaults={})
        location, l_created = Location.objects.get_or_create(name = request.data['location'], defaults={})
        quantity = request.data['quantity']
        quantity_warning = request.data['quantity_warning']
        quantity_alert = request.data['quantity_alert']

        print(serial_numbers)
        if image:
            component_obj.image = image
            component_obj.save()

        # Update other fields
        component_obj.name = name
        component_obj.model = model
        component_obj.description = description
        component_obj.component_type = component_type
        component_obj.department = department
        component_obj.location = location
        component_obj.quantity = quantity
        component_obj.quantity_warning = quantity_warning
        component_obj.quantity_alert = quantity_alert


        serial_container = []
        SerialNumber.objects.filter(component=component_obj).exclude(serial_number__in=serial_numbers).delete()

        for sn in serial_numbers:
            if not SerialNumber.objects.filter(serial_number=sn, component=component_obj).exists():
                serial_container.append(SerialNumber(serial_number=sn, component=component_obj))

        SerialNumber.objects.bulk_create(serial_container)

        component_obj.save()

        return Response({"detail": "%s was update." % name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def delete_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        component = component_obj.get()
        component.delete()
        return Response({"detail": "%s was deleted." % component.name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def info_component_list(request):
    try:
        serial_numbers = request.data.get('serial_numbers', [])
        print(serial_numbers)
        if not serial_numbers :
            return Response({"detail": "No serial numbers provided"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []
        for sn in serial_numbers:
            if SerialNumber.objects.filter(serial_number=sn).exists():
                components = SerialNumber.objects.get(serial_number=sn)
                component_data = SerialNumberWithComponentSerializer(components).data
            else:
                component_data = {
                    'id': None,
                    'component': None,
                    'serial_number': sn
                }
            response_data.append(component_data.copy())
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        return Response({"detail": "Failure, data as your provided is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    