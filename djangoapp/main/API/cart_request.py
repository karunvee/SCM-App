import json
from datetime import datetime
import pytz
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from ..models import *
from ..serializers import *
from .mail import *

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
        requester_name_center = request.data.get('requester_name_center')
        requester_emp_center = request.data.get('requester_emp_center')
        purpose_detail = request.data.get('purpose_detail')
        purpose_type = request.data.get('purpose_type')
       
        rqt = get_object_or_404(Member, emp_id = requester_emp_id)
        prodArea = get_object_or_404(ApprovedRoute, production_area = rqt.production_area)

        if rqt.production_area:
            staff = get_object_or_404(ApprovedRoute, production_area = rqt.production_area).staff_route
            sup = get_object_or_404(ApprovedRoute, production_area = rqt.production_area).supervisor_route
        else:
            staff = get_object_or_404(Member, pk = 1)
            sup = staff

        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        requestReceipt = Request.objects.create(
            requester = rqt, 
            staff_approved = staff, 
            supervisor_approved = sup, 
            purpose_detail = purpose_detail, 
            complete_date = now, 
            pickup_date = now, 
            requester_name_center = requester_name_center, 
            requester_emp_center = requester_emp_center, 
            purpose_type = purpose_type,
            scrap_status = (purpose_type != 'Exchange')
        )

        for item in item_list:
           
            component = get_object_or_404(Component, pk = item['component_id'])
            RequestComponentRelation.objects.create(request=requestReceipt, component=component, qty=item['quantity'])

        try:
            send_mail(prodArea.staff_route.email, requestReceipt.id, prodArea.staff_route.emp_id, rqt.emp_id, rqt.username)
        except Exception as e:
            return Response({"detail": "success", "request_id": requestReceipt.id, "error": f"{str(e)} sending a mail unsuccessfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "success", "request_id": requestReceipt.id}, status=status.HTTP_200_OK)
    except Exception as e:
        requestReceipt.delete()
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_request(request):
    try:
        query_serializer = RequestEmployeeIdQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')
            requests = Request.objects.exclude(status='PickUp').filter(requester__emp_id = emp_id).order_by('-issue_date')
            requests_serializer = RequestSerializer(instance=requests, many=True)
            # Custom Serializer Data
            for req in requests_serializer.data:
                reqRel = RequestComponentRelation.objects.filter(request__id = req['id'])
                req['components'] = []
                for reqRelIndex in reqRel:
                    req['components'].append({
                        'id': reqRelIndex.id,
                        'component_id' : reqRelIndex.component.pk,
                        'component_name' : reqRelIndex.component.name,
                        'component_model' : reqRelIndex.component.model,
                        'component_machine_type' : reqRelIndex.component.machine_type.name,
                        'component_component_type' : reqRelIndex.component.component_type.name,
                        'component_image' : reqRelIndex.component.image_url,
                        'component_consumable' : reqRelIndex.component.consumable,
                        'location' : reqRelIndex.component.location.name,
                        'self_pickup' : reqRelIndex.component.self_pickup,
                        'qty' : reqRelIndex.qty,
                        'serial_numbers': []
                    })
            
            return Response({"detail": "success", "data": requests_serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_my_request(request):
    try:
        query_serializer = RequestQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            request_id = query_serializer.validated_data.get('request_id')
            Request.objects.filter(id = request_id).delete()
            
            return Response({"detail": "success"}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

