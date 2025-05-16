import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
import requests

import pytz
from datetime import datetime, timedelta

from ..models import *
from ..serializers import *

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_po(request):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        # year_expired_date = now - timedelta(days= 36500)
        # PO.objects.filter(issue_date__lte = year_expired_date).delete() 

        po_number = request.data.get('po_number')
        prod_area_name = request.data.get('prod_area_name')
        po_obj = PO.objects.filter(po_number = po_number)
        if not po_obj.exists():
            new_po = PO.objects.create(
                po_number = po_number,
                production_area = get_object_or_404(ProductionArea, prod_area_name = prod_area_name),
            )
            serializer = PoSerializer(new_po)
            return Response({"detail": f"Successfully added {po_number}.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": f"Failure, duplicate data."}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_po(request):
    try:
        po_number = request.data.get('po_number')
        po_obj = PO.objects.filter(po_number = po_number)
        if po_obj.exists():
            serializer = PoSerializer(instance=po_obj.get())
            return Response({"detail": "contained", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": f"Failure, PO not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_grgi(request):
    try:
        query_serializer = ProdAreaNamePaginatorQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            bangkok_tz = pytz.timezone('Asia/Bangkok')

            date_start_str = query_serializer.validated_data.get('date_start')
            date_end_str = query_serializer.validated_data.get('date_end')
            production_area_name = query_serializer.validated_data.get('production_area_name')
            # page_number = query_serializer.validated_data.get('page_number')
            # qty_per_page = query_serializer.validated_data.get('qty_per_page')

            search_value = query_serializer.validated_data.get('search')

            date_start = datetime.strptime(date_start_str, "%m/%d/%Y")
            date_end = datetime.strptime(date_end_str, "%m/%d/%Y")

            # if date_start == date_end:
            date_end = date_end + timedelta(hours=23, minutes=59)
                
            
            if search_value == 'None':
                pdAreaObj = HistoryTrading.objects.filter(component__production_area__prod_area_name = production_area_name, issue_date__range=(date_start, date_end)).order_by('-issue_date')
            else:
                # by only one string
                pdAreaObj = HistoryTrading.objects.filter(
                                                        Q(component__name__icontains=search_value) |
                                                        Q(component__model__icontains=search_value) |
                                                        Q(component__supplier__icontains=search_value) |
                                                        Q(po_number__po_number__icontains=search_value) |
                                                        Q(requester__icontains=search_value) |
                                                        Q(serial_numbers__icontains=search_value),
                                                        component__production_area__prod_area_name = production_area_name, issue_date__range=(date_start, date_end)).order_by('-issue_date') 
            
            total_rows = pdAreaObj.count()

            tt_gr = 0
            tt_gi = 0
            tt_scrap = 0
            for item in pdAreaObj:
                tt_gr = tt_gr + item.gr_qty
                tt_gi = tt_gi + item.gi_qty # tt_gi + (item.gi_qty * -1)
                tt_scrap = tt_scrap + item.scrap_qty
            
            # paginator = Paginator(pdAreaObj, qty_per_page) 
            # page_obj = paginator.get_page(page_number + 1)
            # serializer = HistoryTradingSerializer(instance=page_obj, many=True)
            
            serializer = HistoryTradingSerializer(instance=pdAreaObj, many=True)
            
            return Response({"detail": "success", "data" : serializer.data, "total_rows":  total_rows, "total_gr": tt_gr, "total_gi": tt_gi, "total_scrap": tt_scrap}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_po(request):
    try:
        query_serializer = ProdAreaNameQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            production_area_name = query_serializer.validated_data.get('production_area_name')
            
            poObj = PO.objects.filter(production_area__prod_area_name = production_area_name)
            serializer = PoSerializer(instance=poObj, many=True)
            return Response({"detail": "success", "data" : serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def po_qrcode_search(request):
    try:
        qrcode_search = request.data.get('qrcode_search')
        print(qrcode_search)
        s = get_object_or_404(SerialNumber, serial_number = qrcode_search)
        serializers = PoSerializer(instance = s.po)
        return Response({"detail": "success", "data": serializers.data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(e)
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def po_equipment_search(request):
    try:
        equip = request.data.get('equip')
        print(equip)
        s = SerialNumber.objects.filter(
            Q(component__name__icontains=equip) | Q(component__model__icontains=equip)
        ) 
        po_queryset = PO.objects.filter(id__in=s.values_list('po_id', flat=True))  # Extract related Po objects
        serializers = PoSerializer(instance=po_queryset, many=True)

        return Response({"detail": "success", "data": serializers.data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(e)
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def po_relative_component(request, po_number):
    try:
        historyObj = HistoryTrading.objects.filter(po_number__po_number = po_number)

        if historyObj.exists():
            serializer = HistoryTradingSerializer(historyObj, many=True)
            return Response({"detail": "success", "data" : serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "no data", "data" : {}}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def mod_po(request, pn):
    try:
        po = PO.objects.filter(po_number = pn)
        if request.method == 'PUT':
            new_po_number = request.data.get('new_po_number')
            po.update(po_number = new_po_number)
            return Response({"detail": "success"}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            po.delete()
            return Response({"detail": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Method is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def inventory_list(request):
    try:
        query_serializer = EmployeeIdWithLocationQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')
            location = query_serializer.validated_data.get('location')

            requesterObj = get_object_or_404(Member, emp_id = emp_id)

            if location.upper() == 'ALL':
                compObj = Component.objects.filter(location__production_area = requesterObj.production_area).order_by('name')
            else:
                compObj = Component.objects.filter(location__production_area = requesterObj.production_area, 
                                                   location__name = location).order_by('name')

            serializer_comp = ComponentSerializer(instance = compObj, many=True)

            return Response({"detail": "success", "component_list" : serializer_comp.data }, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"detail": f"Something went wrong, {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def inventory_report_list(request, day_period):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        period_date = now - timedelta(days = int(day_period))

        query_serializer = ProAreaWithLocationQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            production_name = query_serializer.validated_data.get('production_name')
            location = query_serializer.validated_data.get('location')


            if location.upper() == 'ALL':
                inventoryObj = InventoryReport.objects.filter(
                    location__production_area__prod_area_name = production_name,
                    inventory_date__range = (period_date, now)
                    ).order_by('-inventory_date')
            else:
                inventoryObj = InventoryReport.objects.filter(
                    location__production_area__prod_area_name = production_name, 
                    location__name = location,
                    inventory_date__range = (period_date, now)
                    ).order_by('-inventory_date')

            serializer_inv = InventoryReportSerializer(instance = inventoryObj, many=True)

            for inv in serializer_inv.data:
                inv["location_name"] = inv["location"]["name"]

            return Response({"detail": "success", "inventory_report_list" : serializer_inv.data }, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"detail": f"Something went wrong, {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_inventory_report(request):
    try:
        compUpdate = []
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        year_expired_date = now - timedelta(days = 2000)

        emp_id = request.data.get('emp_id')
        rs_status = request.data.get('status')
        missing_list = request.data.get('missing_list')
        location = request.data.get('location')

        for item in missing_list:

            component_obj = get_object_or_404(Component, id = item['id'])
            
            component_obj.last_inventory_date = now
            component_obj.next_inventory_date = now + timedelta(days= 180)

            if component_obj.unique_component:
                array = str([component_obj.last_sn] * item['missingQuantity'])
                component_obj.missing_list = array
            else:   
                component_obj.missing_list = item['missingList']

            compUpdate.append(component_obj)

        staff = get_object_or_404(Member, emp_id = emp_id)


        locationObj = get_object_or_404(Location, name = location)
        locationObj.last_inventory_date = now
        locationObj.save()

        Component.objects.bulk_update(compUpdate, ["last_inventory_date", "next_inventory_date", "missing_list"])
        inventObj = InventoryReport.objects.create(
            staff = staff,
            location = locationObj,
            missing_list = missing_list,
            status = rs_status
        )

        serializer = InventoryReportSerializer(instance = inventObj)
        InventoryReport.objects.filter(inventory_date__lte = year_expired_date).delete() 

        return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def proxy_image(request, equip_type):
    image_url = f"http://10.150.192.16/images/{equip_type}.jpg"
    response = requests.get(image_url, stream=True)
        
        # Check if the image was retrieved successfully
    if response.status_code == 200:
        # Create an HTTP response with the image content
        return HttpResponse(response.content, content_type="image/png")
    else:
        # Return a 404 if the image was not found or an error occurred
        return HttpResponse(status=404)

def deleteAll():
    try:
        HistoryTrading.objects.all().delete()
    except Exception as e:
        return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def inventory_reset(request):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))

        query_serializer = LocationQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            location = query_serializer.validated_data.get('location')
            if location.upper() == 'ALL':

                Component.objects.all().update(
                    last_inventory_date = now,
                    next_inventory_date = now + timedelta(days= 180),
                    missing_list = None
                )
                Location.objects.all().update(
                    last_inventory_date = now
                )
                InventoryReport.objects.all().delete()


            else:
                locationObj = get_object_or_404(Location, name = location)

                invObj = InventoryReport.objects.filter(location = locationObj)
                invObj.delete()

                Component.objects.filter(location = locationObj).update(
                    last_inventory_date = now,
                    next_inventory_date = now + timedelta(days= 180),
                    missing_list = None
                )
                Location.objects.filter(name = location).update(
                    last_inventory_date = now
                )
            return Response({"detail": "success"}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
