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
def component_cart(request):
    try:
        component_list = request.data.get('component_list')
        print(component_list)
        component_obj = Component.objects.filter(pk__in = component_list)
        serializer = ComponentInfoSerializer(instance=component_obj, many=True)

        return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def checkout_cart(request):
    requestReceipt = None
    try:
        item_list = request.data.get('item_list')
        requester_emp_id = request.data.get('requester_emp_id')
        print(item_list, requester_emp_id)

        rqt = get_object_or_404(Member, emp_id = requester_emp_id)
        staff = get_object_or_404(Member, pk = 1)
        sup = get_object_or_404(Member, pk = 1)

        requestReceipt = Request.objects.create(requester = rqt, staff_approved = staff, supervisor_approved = sup)
        for item in item_list:
            print(item)
            component = get_object_or_404(Component, pk = item['component_id'])
            RequestComponentRelation.objects.create(request=requestReceipt, component=component, quantity=item['quantity'])

        return Response({"detail": "success", "request_id": requestReceipt.id}, status=status.HTTP_200_OK)
    except Exception as e:
        requestReceipt.delete()
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_request(request):
    try:
        query_serializer = RequestQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            request_id = query_serializer.validated_data.get('request_id')
            # requests = get_object_or_404(Request, id = request_id)
            requests = Request.objects.all()
            print(requests)
            serializer = RequestSerializer(instance=requests, many=True)

            return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
