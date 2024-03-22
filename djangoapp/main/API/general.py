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

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_po(request):
    try:
        po_number = request.data.get('po_number')
        po_obj = PO.objects.filter(po_number = po_number)
        if not po_obj.exists():
            new_po = PO.objects.create(
                po_number = po_number
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
        query_serializer = ProdAreaNameQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            production_area_name = query_serializer.validated_data.get('production_area_name')
            
            pdAreaObj = HistoryTrading.objects.filter(component__production_area__prod_area_name = production_area_name)
            print(production_area_name)
            print(pdAreaObj)
            serializer = HistoryTradingSerializer(instance=pdAreaObj, many=True)
            return Response({"detail": "success", "data" : serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)