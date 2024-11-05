import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

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
        year_expired_date = now - timedelta(days = 400)

        PO.objects.filter(issue_date__lte = year_expired_date).delete() 

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
def inventory_report(request, location):
    print(location)
    try:
        if location == 'all':
            invtObj = InventoryReport.objects.all().order_by('status').order_by('component__next_invent_date')
        else:
            invtObj = InventoryReport.objects.filter(component__location__name = location).order_by('status').order_by('component__next_invent_date')

        serializer = InventoryReportSerializer(instance = invtObj, many=True)


        return Response({"detail": "no data", "data" : serializer.data }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


def deleteAll():
    HistoryTrading.objects.all().delete()