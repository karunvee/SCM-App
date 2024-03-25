import json
import ast
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


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_approved_route(request):
    try:
        if request.method == 'GET':
            approvedRoute = ApprovedRoute.objects.all()
            serializer = ApprovedRouteSerializer(instance=approvedRoute, many=True)
            return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            query_serializer = ApprovedRouteIdUpdateQuerySerializer(data = request.query_params)
            if query_serializer.is_valid():
                route_id = query_serializer.validated_data.get('route_id')
                staff_id = query_serializer.validated_data.get('staff_id')
                manager_id = query_serializer.validated_data.get('manager_id')

                staff_route = get_object_or_404(Member, pk = staff_id)
                supervisor_route = get_object_or_404(Member, pk = manager_id)

                ApprovedRoute.objects.filter(pk = route_id).update(staff_route = staff_route, supervisor_route = supervisor_route)
                return Response({"detail": "success"}, status=status.HTTP_200_OK)
            
            return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            query_serializer = ApprovedRouteIdQuerySerializer(data = request.query_params)
            if query_serializer.is_valid():
                route_id = query_serializer.validated_data.get('route_id')
                ApprovedRoute.objects.filter(pk = route_id).delete()

                return Response({"detail": "success"}, status=status.HTTP_200_OK)
            
            return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def approval_list(request):
    try:
        query_serializer = EmployeeIdQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')

            approver = get_object_or_404(Member, emp_id = emp_id)
            route = get_object_or_404(ApprovedRoute, production_area = approver.production_area)
            
            if route.staff_route == approver:
                request_obj = Request.objects.filter(staff_approved = approver, status = 'Requested')
            elif route.supervisor_route == approver:
                request_obj = Request.objects.filter(supervisor_approved = approver, status = 'Staff')
            else:
                return Response({"detail": "Not found you route"}, status=status.HTTP_404_NOT_FOUND)
            
            requests_serializer = RequestSerializer(instance=request_obj, many=True)
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
                        'qty' : reqRelIndex.qty,
                        'serial_numbers': []
                    })

            return Response({"detail": "success", "data": requests_serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def approved_order(request):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))

        request_id = request.data.get('request_id')
        emp_id = request.data.get('emp_id')
        method = request.data.get('method')
        serial_numbers = request.data.get('serial_numbers')
       
        member = get_object_or_404(Member, emp_id = emp_id)

        request_obj = Request.objects.filter(id = request_id)
    
        member_requests = request_obj.filter(
        models.Q(requester=member) |
        models.Q(staff_approved=member) |
        models.Q(supervisor_approved=member)
        )
        if member_requests.exists():
            if method == 'approve':
                if not request_obj.get().update_status_to_next():
                    return Response({"detail": "Cannot update status"}, status=status.HTTP_400_BAD_REQUEST)
                
            elif method == 'success':
                
                SerialNumber.objects.filter(serial_number__in = serial_numbers).update(request = request_obj.get())
                request_obj.update(complete_date = now)
                if not request_obj.get().update_status_to_next():
                    return Response({"detail": "Cannot update status"}, status=status.HTTP_400_BAD_REQUEST)
                
            elif method == 'reject':
                request_obj.update(rejected = True)

            elif method == 'reset':
                request_obj.update(rejected = False)

            else:
                request_obj.delete()

            return Response({"detail": "success"}, status=status.HTTP_200_OK)
            
        return Response({"detail": "Permission denied"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def preparing_list(request):
    try:
        request_obj = Request.objects.filter(status__in = ['Manager' ,'Preparing'])
        requests_serializer = RequestSerializer(instance=request_obj, many=True)
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
                    'location' : reqRelIndex.component.location.name,
                    'qty' : reqRelIndex.qty,
                    'serial_numbers': []
                })

        return Response({"detail": "success", "data": requests_serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_in(request):
    query_serializer = RequestQuerySerializer(data = request.query_params)

    if query_serializer.is_valid():
        request_id = query_serializer.validated_data.get('request_id')
        requests = Request.objects.filter(id = request_id, status='Success')
        if not requests.exists():
            return Response({"detail": "This Request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        requests_serializer = RequestSerializer(instance = requests, many=True)
        for req in requests_serializer.data:
            reqRel = RequestComponentRelation.objects.filter(request__id = req['id'])
            req['components'] = []
            for reqRelIndex in reqRel:
                serial_numbers = SerialNumber.objects.filter(request__id = req['id'], component__pk = reqRelIndex.component.pk)
                serializers_serial_numbers = SerialNumberSerializer(instance=serial_numbers, many=True)
                req['components'].append({
                    'id': reqRelIndex.id,
                    'component_id' : reqRelIndex.component.pk,
                    'component_name' : reqRelIndex.component.name,
                    'component_model' : reqRelIndex.component.model,
                    'component_machine_type' : reqRelIndex.component.machine_type.name,
                    'component_component_type' : reqRelIndex.component.component_type.name,
                    'component_image' : reqRelIndex.component.image_url,
                    'qty' : reqRelIndex.qty,
                    'serial_numbers': serializers_serial_numbers.data,
                })

        return Response({"detail": "success", "data": requests_serializer.data}, status=status.HTTP_200_OK)
        
    
    return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def pick_up(request):
    try:
        request_id = request.data.get('request_id')
        emp_name = request.data.get('emp_name')

        request_obj = get_object_or_404(Request, id = request_id)
        
        history_items = []
        print('hit')
        component_relate = RequestComponentRelation.objects.filter(request = request_obj)
        for cr in component_relate:
            serial_numbers_obj = SerialNumber.objects.filter(request__id = request_obj.id, component = cr.component)
            serial_numbers = []
            for sn in serial_numbers_obj:
                serial_numbers.append(sn.serial_number)
            # serializers_serial_numbers = SerialNumberOnlySnSerializer(instance=serial_numbers_obj, many=True)

            history_items.append(HistoryTrading(
                    requester = request_obj.requester.username,
                    staff_approved = request_obj.staff_approved.username,
                    supervisor_approved = request_obj.supervisor_approved.username,
                    trader = emp_name,
                    gr_qty = 0,
                    gi_qty = (-cr.qty),
                    purpose_detail=request_obj.purpose_detail,
                    component=cr.component,
                    request_id = request_obj.id,
                    serial_numbers = serial_numbers
                )) 
        if not request_obj.update_status_to_next():
            return Response({"detail": "Cannot update status"}, status=status.HTTP_400_BAD_REQUEST)
        
        HistoryTrading.objects.bulk_create(history_items)

        return Response({"detail": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
