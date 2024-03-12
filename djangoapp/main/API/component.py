import json
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from ..models import *
from ..serializers import *

@api_view(['GET'])
def component_list(request):
    component_list = Component.objects.all()
    serializers = ComponentSerializer(instance=component_list, many=True)
    context = {
        'component_list': serializers.data
    }
    return Response(context)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def component_filter(request):
    try:
        query_serializer = ComponentFilterQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            component_type_content = query_serializer.validated_data.get('component_type_content')
            machine_type_content = query_serializer.validated_data.get('machine_type_content')
            print('::', component_type_content, machine_type_content)
            component_obj = Component.objects.all()
            if component_type_content != 'All':   
                component_obj = component_obj.filter(component_type__name = component_type_content)
            if machine_type_content != 'All':
                component_obj = component_obj.filter( machine_type__name = machine_type_content)

            serializers = ComponentWithoutSerialsSerializer(instance=component_obj, many=True)

            return Response({"detail": "success", "data": serializers.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def component_get_one(request):
    try:
        query_serializer = ComponentQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            component_obj = get_object_or_404(Component, pk = query_serializer.validated_data.get('component_id'))
            serializers = ComponentSerializer(instance=component_obj)
            return Response({"detail": "success", "data": serializers.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_component(request):
    try:
        image = request.data.get('image')
        name = request.data.get('name')
        model = request.data.get('model')
        # po_number = request.data['po_number']
        # serial_numbers = request.data.get('serial_numbers').split(',')
        description = request.data.get('description')
        consumable = request.data.get('consumable')
        
        machine_type, ct_created = MachineType.objects.get_or_create(name=request.data.get('machine_type'), defaults={})
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
            consumable=consumable,
            description=description,
            machine_type=machine_type,
            component_type=component_type,
            department=department,
            location=location,
            quantity=quantity,
            quantity_warning=quantity_warning,
            quantity_alert=quantity_alert,
            )

            serializer = ComponentSerializer(component_obj)
            return Response({"detail": f"Successfully added {name}.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Failure, duplicate data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        print(request.data)
        component_obj = component_obj.first()
        image = request.data.get('image')
        name = request.data.get('name')
        model = request.data.get('model')
        # po_number = request.data['po_number']
        # serial_numbers = request.data['serial_numbers'].split(',')
        description = request.data.get('description')
        consumable = request.data.get('consumable')

        machine_type, ct_created = MachineType.objects.get_or_create(name=request.data.get('machine_type'), defaults={})
        component_type, ct_created = ComponentType.objects.get_or_create(name=request.data.get('component_type'), defaults={})
        department, d_created = Department.objects.get_or_create(name=request.data.get('department'), defaults={})
        location, l_created = Location.objects.get_or_create(name=request.data.get('location'), defaults={})
        quantity = request.data.get('quantity')
        quantity_warning = request.data.get('quantity_warning')
        quantity_alert = request.data.get('quantity_alert')


        if image:
            component_obj.image = image
            component_obj.save()

        # Update other fields
        component_obj.name = name
        component_obj.model = model
        component_obj.consumable = bool(consumable)
        component_obj.description = description
        component_obj.machine_type = machine_type
        component_obj.component_type = component_type
        component_obj.department = department
        component_obj.location = location
        component_obj.quantity = SerialNumber.objects.filter(component = component_obj).count()
        component_obj.quantity_warning = quantity_warning
        component_obj.quantity_alert = quantity_alert


        component_obj.save()

        return Response({"detail": "%s was update." % name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        component = component_obj.get()
        component.delete()
        return Response({"detail": "%s was deleted." % component.name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_item(request):
    try:
        component_id = request.data.get('component_id')
        print(request.data.get('serial_numbers'))
        serial_numbers = request.data.get('serial_numbers')
        po_number = request.data.get('po_number')

        component_obj = get_object_or_404(Component, pk = component_id)
        
        serial_container = []
        for sn in serial_numbers:
            if SerialNumber.objects.filter(serial_number = sn).exists():
                return Response({"detail": f"Duplicate data, '{sn}' already exist in table."}, status=status.HTTP_409_CONFLICT)
            serial_container.append(SerialNumber(serial_number=sn, component=component_obj, po = PO.objects.get(po_number = po_number)))
        SerialNumber.objects.bulk_create(serial_container)

        component_obj.quantity = SerialNumber.objects.filter(component = component_obj).count()
        print(component_obj.quantity)
        component_obj.save()

        return Response({"detail": f"Added items to PO: {po_number}"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_item(request):
    try:
        query_serializer = ComponentQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            component_id = query_serializer.validated_data.get('component_id')
            
            serial_number_obj = SerialNumber.objects.filter(component__pk = component_id)
            serializer = SerialNumberSerializer(instance = serial_number_obj, many=True)

            return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
