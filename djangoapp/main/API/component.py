import json
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import pytz
from datetime import datetime, timedelta

from ..models import *
from ..serializers import *

@api_view(['GET'])
def component_list(request):
    try:
        query_serializer = ComponentProdNameQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            production_name = query_serializer.validated_data.get('production_name')
            component_list = Component.objects.filter(production_area__prod_area_name = production_name).order_by('name')
            serializers = ComponentWithoutSerialsSerializer(instance=component_list, many=True)

            return Response({"detail": "success", "data": serializers.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def location_inventory(request, day_period):
    now = datetime.now(pytz.timezone('Asia/Bangkok'))
    period_date = now - timedelta(days = int(day_period))
            # InventoryReport.objects.filter(inventory_date__lte = year_expired_date).delete() 
    try:
        query_serializer = ComponentProdNameQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            production_name = query_serializer.validated_data.get('production_name')
            locations = Location.objects.filter(production_area__prod_area_name = production_name, last_inventory_date__lte = period_date).order_by('name')
            serializers = LocationSerializer(instance=locations, many=True)

            return Response({"detail": "success", "data": serializers.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def component_filter(request):
    try:
        query_serializer = ComponentFilterQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            component_type_content = query_serializer.validated_data.get('component_type_content')
            machine_type_content = query_serializer.validated_data.get('machine_type_content')
            production_name = query_serializer.validated_data.get('production_name')
            print(production_name)
            print('::', component_type_content, machine_type_content)
            component_obj = Component.objects.filter(production_area__prod_area_name = production_name).order_by('name')
            if component_type_content != 'All':   
                component_obj = component_obj.filter(component_type__name = component_type_content).order_by('name')
            if machine_type_content != 'All':
                component_obj = component_obj.filter( machine_type__name = machine_type_content).order_by('name')

            comp_serializers = ComponentSerializer(instance=component_obj, many=True)

            for comp in comp_serializers.data:
                ssRel = LineSafetyStockRelation.objects.filter(component__id = comp['id'])
                comp['line_safety_stock'] = []
                for ssRelIndex in ssRel:
                    comp['line_safety_stock'].append({
                        'id': ssRelIndex.id,
                        'line_name': ssRelIndex.line.line_name,
                        'safety_number': ssRelIndex.safety_number,
                        'modify_date': ssRelIndex.modify_date,
                        'added_date': ssRelIndex.added_date,
                        'modify_member': ssRelIndex.modify_member,
                        'added_member': ssRelIndex.added_member,
                    })

            return Response({"detail": "success", "data": comp_serializers.data}, status=status.HTTP_200_OK)
        
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
        emp_id = request.data.get('emp_id')
        image = request.data.get('image')
        name = request.data.get('name')
        model = request.data.get('model')

        description = request.data.get('description')
        self_pickup = request.data.get('self_pickup')
        unique_component = request.data.get('unique_component')
        equipment_type = request.data.get('equipment_type')
        price = request.data.get('price')
        supplier = request.data.get('supplier')

        comObj = Component.objects.filter(model__iexact = model)
        if comObj.exists():
            serializer_comp_duplicate = ComponentSerializer(instance = comObj)
            return Response({"detail": f"Duplicated model, This model already exist in the storage, please recheck.", "data": serializer_comp_duplicate.data}, status=status.HTTP_409_CONFLICT)

        production_area = get_object_or_404(ProductionArea, prod_area_name=request.data.get('production_name'))

        machine_type = get_object_or_404(MachineType, name=request.data.get('machine_type'), production_area = production_area)
        component_type = get_object_or_404(ComponentType, name=request.data.get('component_type'))
        department = get_object_or_404(Department, name=request.data.get('department'))
        location = get_object_or_404(Location, name=request.data.get('location'), production_area = production_area)
        member = get_object_or_404(Member, emp_id = emp_id)

        quantity = request.data.get('quantity')
        quantity_warning = request.data.get('quantity_warning')
        quantity_alert = request.data.get('quantity_alert')

        if not Component.objects.filter(name=name, model=model, department__name=request.data.get('department')).exists():
            component_obj = Component.objects.create(
            image=image,
            name=name,
            model=model,
            self_pickup = self_pickup.lower() == 'true',
            unique_component = unique_component.lower() == 'true',
            description=description,
            equipment_type=equipment_type.upper(),
            price=price,
            supplier=supplier,
            machine_type=machine_type,
            component_type=component_type,
            department=department,
            location=location,
            quantity=quantity,
            quantity_warning=quantity_warning,
            quantity_alert=quantity_alert,
            production_area=production_area,
            added_member=member,
            modify_member=member,
            )

            serializer = ComponentSerializer(component_obj)
            return Response({"detail": f"Successfully added {name}.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Failure, duplicate data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        print(request.data)
        component_obj = component_obj.first()
        emp_id = request.data.get('emp_id')
        image = request.data.get('image')
        name = request.data.get('name')
        model = request.data.get('model')
        # po_number = request.data['po_number']
        # serial_numbers = request.data['serial_numbers'].split(',')
        description = request.data.get('description')
        self_pickup = request.data.get('self_pickup')
        unique_component = request.data.get('unique_component')
        equipment_type = request.data.get('equipment_type')
        price = request.data.get('price')
        supplier = request.data.get('supplier')

        comObj = Component.objects.filter(model__iexact = model).exclude(pk = pk)
        if comObj.exists():
            serializer_comp_duplicate = ComponentWithoutSerialsSerializer(instance = comObj.get())
            return Response({"detail": f"Duplicated model, This model already exist in the storage, please recheck.", "data": serializer_comp_duplicate.data}, status=status.HTTP_409_CONFLICT)

        machine_type, ct_created = MachineType.objects.get_or_create(name=request.data.get('machine_type'), defaults={})
        component_type, ct_created = ComponentType.objects.get_or_create(name=request.data.get('component_type'), defaults={})
        department, d_created = Department.objects.get_or_create(name=request.data.get('department'), defaults={})
        location, l_created = Location.objects.get_or_create(name=request.data.get('location'), defaults={})
        quantity = request.data.get('quantity')
        quantity_warning = request.data.get('quantity_warning')
        quantity_alert = request.data.get('quantity_alert')

        member = get_object_or_404(Member, emp_id = emp_id)
        if image:
            component_obj.image = image
            component_obj.save()

        if unique_component.lower() == 'true':
            qty = component_obj.quantity
        else:
            qty = SerialNumber.objects.filter(component = component_obj).count()
        # Update other fields
        component_obj.name = name
        component_obj.model = model
        component_obj.self_pickup = self_pickup.lower() == 'true'
        component_obj.unique_component = unique_component.lower() == 'true'
        component_obj.description = description
        component_obj.equipment_type = equipment_type.upper()
        component_obj.price = price
        component_obj.supplier = supplier
        component_obj.machine_type = machine_type
        component_obj.component_type = component_type
        component_obj.department = department
        component_obj.location = location
        component_obj.quantity = qty
        component_obj.quantity_warning = quantity_warning
        component_obj.quantity_alert = quantity_alert
        component_obj.modify_member = member


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
        # print(request.data.get('serial_numbers'))
        serial_numbers = request.data.get('serial_numbers')
        po = PO.objects.get(po_number = request.data.get('po_number'))

        emp_id = request.data.get('emp_id')
        trader = get_object_or_404(Member, emp_id = emp_id)
        component_obj = get_object_or_404(Component, pk = component_id)
        
        serial_container = []
        for sn in serial_numbers:
            if SerialNumber.objects.filter(serial_number = sn).exists():
                return Response({"detail": f"Duplicate data, '{sn}' already exist in table."}, status=status.HTTP_409_CONFLICT)
            serial_container.append(SerialNumber(serial_number=sn, component=component_obj, po = po))
        SerialNumber.objects.bulk_create(serial_container)

        balance = SerialNumber.objects.filter(component = component_obj).count()
        component_obj.quantity = balance
        # print('last_sn' , serial_numbers[len(serial_numbers) - 1])
        component_obj.last_sn = serial_numbers[len(serial_numbers) - 1]
        # print(component_obj.quantity)
        component_obj.save()

        HistoryTrading.objects.create(
                    requester = "",
                    staff_approved = "",
                    supervisor_approved = "",
                    trader = trader.name,
                    left_qty = balance,
                    gr_qty = len(serial_numbers),
                    gi_qty = 0,
                    purpose_detail="Add",
                    component=component_obj,
                    request_id = "",
                    po_number = po,
                    serial_numbers = serial_numbers
            )

        return Response({"detail": f"Added items to PO: {request.data.get('po_number')}"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_item_unique(request):
    try:
        component_id = request.data.get('component_id')
        quantity = int(request.data.get('quantity'))
        po = PO.objects.get(po_number = request.data.get('po_number'))

        emp_id = request.data.get('emp_id')
        trader = get_object_or_404(Member, emp_id = emp_id)
        component_obj = get_object_or_404(Component, pk = component_id)
    
        balance = component_obj.quantity + quantity
        component_obj.quantity = balance

        sn = f"{trader.production_area.detail}{component_obj.unique_id}-@UNIQUE"  
        component_obj.last_sn = sn

        component_obj.save()

        if not SerialNumber.objects.filter(serial_number = sn).exists():
            SerialNumber.objects.create(serial_number=sn, component=component_obj, po = po)

        HistoryTrading.objects.create(
                    requester = "",
                    staff_approved = "",
                    supervisor_approved = "",
                    trader = trader.name,
                    left_qty = balance,
                    gr_qty = quantity,
                    gi_qty = 0,
                    purpose_detail="Add",
                    component=component_obj,
                    request_id = "",
                    po_number = po,
                    serial_numbers = ''
            )

        return Response({"detail": f"Added items to PO: {request.data.get('po_number')}"}, status=status.HTTP_200_OK)
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
            serializer = SerialNumberWithStrPoSerializer(instance = serial_number_obj, many=True)
            print(serializer.data)
            return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


def generate_unique_sn(component_id, i, last_sn):
    
    # if not snExist:
    #     last_id = i
    # else:
    # Get the maximum serial number associated with the given component
    last_serial_number = SerialNumber.objects.filter(component__pk=component_id).order_by('-serial_number').first()

    if last_serial_number:
        print(last_serial_number.serial_number[9:])
        last_id = int(last_serial_number.serial_number[9:], 36) + i # Extract numeric part of the ID
    else:
        # If no serial number exists yet
        if last_sn:
            last_id = int(last_sn[9:], 36) + i
        else:
            last_id = i

    # Define the characters to be used in the ID
    characters = '0123456789abcdefghijklmnopqrstuvwxyz'

    # Get the maximum possible ID based on the number of characters available
    max_length = 7
    max_id = len(characters) ** max_length

    if last_id >= max_id:
        last_id = 0
        # raise ValueError("Maximum number of IDs reached")
    

    # Increment the last ID
    next_id = last_id + 1

    # Convert the incremented ID to a 5-character base36 string
    id_string = ''
    while next_id:
        next_id, remainder = divmod(next_id, len(characters))
        id_string = characters[remainder] + id_string

    # Pad the ID with zeros if necessary
    id_string = id_string.zfill(max_length)

    # Combine the component prefix with the generated ID
    return f"{id_string}".upper()


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_serial_number(request):
    try:
        query_serializer = GenerateSerialNumberQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')
            component_id = query_serializer.validated_data.get('component_id')
            quantity = query_serializer.validated_data.get('quantity')

            member = get_object_or_404(Member, emp_id = emp_id)
            component =  get_object_or_404(Component, pk = component_id)

            last_sn = component.last_sn
    
            sn_list = []
            for i in range(int(quantity)):
                txt = f"{member.production_area.detail}{component.unique_id}-{generate_unique_sn(component_id, i, last_sn)}"  
                print(txt)
                sn_list.append(txt)

            return Response({"detail": "success", "data": sn_list}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_unique_id(request):
    try:
        component_id = request.data.get('component_id')
        unique_id = request.data.get('unique_id')
        prod_name = request.data.get('prod_name')

        print(component_id, unique_id, prod_name)
        comp = Component.objects.filter(production_area__prod_area_name = prod_name)

        if component_id == 0:
            if comp.filter(unique_id = unique_id).exists():
                return Response({"detail": "This Unique ID have been used"}, status=status.HTTP_409_CONFLICT)
            return Response({"detail": "This Unique ID is OK."}, status=status.HTTP_200_OK)
        else:
            if comp.exclude(id = component_id).filter(unique_id = unique_id).exists():
                return Response({"detail": "This Unique ID have been used"}, status=status.HTTP_409_CONFLICT)
            return Response({"detail": "This Unique ID is OK."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_serial_number_list(request):
    try:
        item_list = request.data.get('item_list')
        component_list = request.data.get('component_list')
        print(item_list, component_list)
        item_used = []
        lists = []
        component_counts = {}

        for component in component_list:    
            for serial_number in item_list:
                try:
                    compObj = Component.objects.get(pk = component)
                    sn = SerialNumber.objects.filter(serial_number=serial_number["sn"], component = compObj)
                    if sn.exists():
                        item_used.append(serial_number["sn"])
                        if compObj.unique_component:
                            component_counts[component] = serial_number["qty"]
                        else:
                            component_counts[component] = component_counts.get(component, 0) + 1
                        
                    else:
                        component_counts[component] = component_counts.get(component, 0)
                        
                        
                except SerialNumber.DoesNotExist:
                    continue  # Skip if the serial number doesn't exist in the database

            lists.append({
                "id": component,
                "qty": component_counts[component],
                "unique_component": compObj.unique_component
            })
        s = set(item_used)
        diff = [x["sn"] for x in item_list if x["sn"] not in s]

        return Response({"detail": "success", "data": lists, "diff": diff}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def component_model_exist_checking(request, model):
        comObj = Component.objects.filter(model__iexact = model)
        if comObj.exists():
            serializer_comp_duplicate = ComponentSerializer(instance = comObj)
            return Response({"detail": f"Duplicated model, This model already exist in the storage, please recheck.", "data": serializer_comp_duplicate.data}, status=status.HTTP_409_CONFLICT)
        return Response({"detail": f"pass"}, status=status.HTTP_202_ACCEPTED)

