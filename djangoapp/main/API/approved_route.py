import json
import ast
from datetime import datetime
import pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Exists, OuterRef
from datetime import datetime, timedelta
import time
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import F

from ..models import *
from ..serializers import *
from .mail import *

@api_view(['GET', 'PUT', 'POST', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_approved_route(request):
    try:
        if request.method == 'GET':
            query_serializer = EmployeeIdQuerySerializer(data = request.query_params)
            if query_serializer.is_valid():
                emp_id = query_serializer.validated_data.get('emp_id')
                member_req = get_object_or_404(Member, emp_id = emp_id)

                if member_req.is_administrator:
                    approvedRoute = ApprovedRoute.objects.all()
                else:
                    approvedRoute = ApprovedRoute.objects.filter(production_area=member_req.production_area)

                serializer = ApprovedRouteSerializer(instance=approvedRoute, many=True)
                return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            
            return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PUT':
            query_serializer = ApprovedRouteIdUpdateQuerySerializer(data = request.query_params)
            if query_serializer.is_valid():
                route_id = query_serializer.validated_data.get('route_id')
                staff_id = query_serializer.validated_data.get('staff_id')
                supervisor_id = query_serializer.validated_data.get('supervisor_id')
                manager_id = query_serializer.validated_data.get('manager_id')

                staff = get_object_or_404(Member, pk = staff_id)
                supervisor = get_object_or_404(Member, pk = supervisor_id)
                manager = get_object_or_404(Member, pk = manager_id)

                ApprovedRoute.objects.filter(pk = route_id).update(staff_route = staff, supervisor_route = supervisor, approve_route = manager)
                return Response({"detail": "success"}, status=status.HTTP_200_OK)
            
            return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'POST':
            area_name = request.data.get('area_name')
            description = request.data.get('description')
            detail = request.data.get('detail')
            staff_id = request.data.get('staff_id')
            supervisor_id = request.data.get('supervisor_id')
            manager_id = request.data.get('manager_id')
            print(area_name, description, detail)
            prdArea = ProductionArea.objects.create(
                prod_area_name = area_name,
                description = description,
                detail = detail
            )
            print(prdArea)
            ApprovedRoute.objects.create(
                production_area = prdArea,
                staff_route = Member.objects.get(pk = staff_id),
                supervisor_route = Member.objects.get(pk = supervisor_id),
                approve_route = Member.objects.get(pk = manager_id)
            )
            return Response({"detail": "success"}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            query_serializer = ApprovedRouteIdQuerySerializer(data = request.query_params)
            if query_serializer.is_valid():
                route_id = query_serializer.validated_data.get('route_id')
                ap = ApprovedRoute.objects.get(pk = route_id)
                ProductionArea.objects.filter(pk = ap.production_area.pk).delete()
                ap.delete()
                return Response({"detail": "success"}, status=status.HTTP_200_OK)
            
            return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Data format or Method are invalid"}, status=status.HTTP_400_BAD_REQUEST)     
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_your_approved_route(request):
    try:
        query_serializer = ComponentProdNameQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            production_name = query_serializer.validated_data.get('production_name')
            approvedRoute = get_object_or_404(ApprovedRoute, production_area__prod_area_name=production_name)
            serializer = ApprovedRouteSerializer(instance=approvedRoute)
            return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)

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
            print(approver.production_area)
            route = get_object_or_404(ApprovedRoute, production_area = approver.production_area)
            
            if route.staff_route == approver and route.supervisor_route != approver:
                request_obj = Request.objects.filter(requester__production_area = approver.production_area, staff_approved = approver, status = 'Requested').order_by('-issue_date')
            elif route.staff_route != approver and route.supervisor_route == approver:
                request_obj = Request.objects.filter(requester__production_area = approver.production_area, supervisor_approved = approver, status = 'Staff').order_by('-issue_date')
            elif route.staff_route == approver and route.supervisor_route == approver:
                request_obj = Request.objects.filter(requester__production_area = approver.production_area, status__in = ['Requested', 'Staff']).order_by('-issue_date')
            else:
                # Administrator
                if not approver.is_supervisor:
                    return Response({"detail": "Not found, you have no approved route."}, status=status.HTTP_404_NOT_FOUND)
                request_obj = Request.objects.filter(status__in = ['Requested', 'Staff']).order_by('-issue_date')
            
            print(approver.production_area)

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
        prodArea = get_object_or_404(ApprovedRoute, production_area = member.production_area)

        request_obj = Request.objects.filter(id = request_id)

        if not request_obj.exists():
            return Response({"detail": f"Request ID [{request_id}] not found."}, status=status.HTTP_404_NOT_FOUND)
    
        # member_requests = request_obj.filter(
        #     models.Q(requester=member) |
        #     models.Q(staff_approved=member) |
        #     models.Q(supervisor_approved=member)
        # )
        if member.is_staff:
            requestData = request_obj.get()
            if method == 'approve':
                if not requestData.update_status_to_next():
                    return Response({"detail": "Cannot update status"}, status=status.HTTP_400_BAD_REQUEST)
                r_status = requestData.get_status_index()
                if r_status == 1:
                    try:
                        send_mail(prodArea.supervisor_route, requestData)
                    except Exception as e:
                        return Response({"detail": "success", "mail": f"{str(e)} sending a mail unsuccessfully."}, status=status.HTTP_200_OK)
                if r_status == 2:
                    if requestData.self_pickup:
                        requestData.delete()

            elif method == 'success':
                r_status = requestData.get_status_index()

                sn_list = [item['sn'] for item in serial_numbers if not item['unique_component'] ] 
                SerialNumber.objects.filter(serial_number__in = sn_list).update(request = requestData)
                requestData = request_obj.get()
                requestData.complete_date = now
                requestData.pickup_status = True
                requestData.save()

                if r_status >= 2:
                    if not requestData.update_status_to_next():
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
def approved_order_byMail(request):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))

        query_serializer = ApproveByMailQuerySerializer(data = request.query_params)

        if query_serializer.is_valid():

            request_id = query_serializer.validated_data.get('request_id')
            emp_id = query_serializer.validated_data.get('emp_id')

            member = get_object_or_404(Member, emp_id = emp_id)
            prodArea = get_object_or_404(ApprovedRoute, production_area = member.production_area)


            request_obj = Request.objects.filter(id = request_id)

        
            member_requests = request_obj.filter(
            models.Q(requester=member) |
            models.Q(staff_approved=member) |
            models.Q(supervisor_approved=member)
            )
            if member_requests.exists():
                requestData = request_obj.get()

                if requestData.get_status_index() < 2:
                    if not requestData.update_status_to_next():
                        return Response({"detail": "Cannot update status"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    r_status = requestData.get_status_index()
                    if r_status == 1:
                        try:
                            send_mail(prodArea.supervisor_route, requestData)
                        except Exception as e:
                            return Response({"detail": "success", "mail": f"{str(e)} sending a mail unsuccessfully."}, status=status.HTTP_200_OK)
                    if r_status == 2:
                        if requestData.self_pickup:
                            requestData.delete()
                            print('self pick-up already !!! delete this request')

                return redirect(f"https://thwgrwarroom.deltaww.com/scm/approved/by_mail?request_id={request_id}&result=success")
                
            return redirect(f"https://thwgrwarroom.deltaww.com/scm/approved/by_mail?request_id={request_id}&result=not_found")
        
        return redirect(f"https://thwgrwarroom.deltaww.com/scm/approved/by_mail?request_id={request_id}&result=error")
    except Exception as e:
        print(str(e))
        return redirect(f"https://thwgrwarroom.deltaww.com/scm/approved/by_mail?request_id={request_id}&result=error")
    
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
def all_request_list(request):
    try:
        query_serializer = EmployeeIdQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')

            requesterObj = get_object_or_404(Member, emp_id = emp_id)

            request_obj = Request.objects.filter(requester__production_area = requesterObj.production_area).order_by('-issue_date')
            
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
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_in(request):
    query_serializer = RequestQuerySerializer(data = request.query_params)

    if query_serializer.is_valid():
        request_id = query_serializer.validated_data.get('request_id')
        requests = Request.objects.filter(id = request_id)
        if not requests.exists():
            print(request_id)
            return Response({"detail": "This Request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        requests_serializer = RequestSerializer(instance = requests, many=True)
        for req in requests_serializer.data:
            reqRel = RequestComponentRelation.objects.filter(request__id = req['id'])
            req['components'] = []
            for reqRelIndex in reqRel:
                serial_numbers = SerialNumber.objects.filter(request__id = req['id'], component__pk = reqRelIndex.component.pk)
                serial_numbers_inhouse = SerialNumber.objects.filter(component__pk = reqRelIndex.component.pk)
                serializers_serial_numbers = SerialNumberSerializer(instance=serial_numbers, many=True)
                serializers_serial_numbers_inhouse = SerialNumberSerializer(instance=serial_numbers_inhouse, many=True)
                req['components'].append({
                    'id': reqRelIndex.id,
                    'component_id' : reqRelIndex.component.pk,
                    'component_name' : reqRelIndex.component.name,
                    'component_model' : reqRelIndex.component.model,
                    'component_unique' : reqRelIndex.component.unique_component,
                    'component_last_sn' : reqRelIndex.component.last_sn,
                    'component_machine_type' : reqRelIndex.component.machine_type.name,
                    'component_component_type' : reqRelIndex.component.component_type.name,
                    'component_image' : reqRelIndex.component.image_url,
                    'location' : reqRelIndex.component.location.name,
                    'qty' : reqRelIndex.qty,
                    'serial_numbers': serializers_serial_numbers.data,
                    'serial_numbers_inhouse': serializers_serial_numbers_inhouse.data,
                })

        return Response({"detail": "success", "data": requests_serializer.data}, status=status.HTTP_200_OK)
        
    
    return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def scrap(request, request_id):
    try:
        scrap_list = request.data.get('scrap_list')

        request_obj = get_object_or_404(Request, id = request_id)

        request_obj.scrap_list = scrap_list
        request_obj.scrap_status = True
        request_obj.save()
        return Response({"detail": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def self_pick_up_list(request, emp_id):
    try:
        req = Request.objects.filter(requester__emp_id = emp_id, self_pickup = False).order_by('-issue_date')
        requests_serializer = RequestSerializer(instance=req, many=True)
        
        req_list = []
        # Custom Serializer Data
        for req in requests_serializer.data:
            enable_pickup = True
            reqRel = RequestComponentRelation.objects.filter(request__id = req['id'])
            req['components'] = []
            all_self_pickup = True
            
            for reqRelIndex in reqRel:
                req['components'].append({
                    'id': reqRelIndex.id,
                    'component_id' : reqRelIndex.component.pk,
                    'component_name' : reqRelIndex.component.name,
                    'component_model' : reqRelIndex.component.model,
                    'component_machine_type' : reqRelIndex.component.machine_type.name,
                    'component_component_type' : reqRelIndex.component.component_type.name,
                    'component_image' : reqRelIndex.component.image_url,
                    'unique_component' : reqRelIndex.component.unique_component,
                    'location' : reqRelIndex.component.location.name,
                    'qty' : reqRelIndex.qty,
                    'serial_numbers': []
                })
                if not reqRelIndex.component.self_pickup: 
                    enable_pickup = False
                    break
                
                if not reqRelIndex.component.self_pickup:
                    all_self_pickup = False

            req['all_self_pickup'] = all_self_pickup

            if enable_pickup:
                req_list.append(req)

        return Response({"detail": "success", "data": req_list}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def pick_up(request):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        year_expired_date = now - timedelta(days = 2000)

        request_id = request.data.get('request_id')
        emp_name = request.data.get('emp_name')

        request_obj = get_object_or_404(Request, id = request_id)
        history_items = []
        component_relate = RequestComponentRelation.objects.filter(request = request_obj)
        for cr in component_relate:
            serial_numbers_obj = SerialNumber.objects.filter(request__id = request_obj.id, component = cr.component)
            serial_numbers = []
            for sn in serial_numbers_obj:
                serial_numbers.append(sn.serial_number)
            # serializers_serial_numbers = SerialNumberOnlySnSerializer(instance=serial_numbers_obj, many=True)

            if(request_obj.requester_name_center):
                request_name = f"{request_obj.requester_emp_center}, {request_obj.requester_name_center} ({request_obj.requester.username})"
            else:
                request_name = f"{request_obj.requester.emp_id}, {request_obj.requester.username}"


            if(request_obj.scrap_list and not cr.component.unique_component):
                scrap_serial_numbers = ast.literal_eval(request_obj.scrap_list)
            else:
                scrap_serial_numbers = []

            scrap_list = [item['sn'] for item in scrap_serial_numbers if item['component_id'] == cr.component.pk]

            history_items.append(HistoryTrading(
                    requester = request_name,
                    request_date=request_obj.issue_date,
                    staff_approved = request_obj.staff_approved.username,
                    supervisor_approved = request_obj.supervisor_approved.username,
                    trader = emp_name,
                    left_qty = (cr.component.quantity - cr.qty),
                    gr_qty = 0,
                    gi_qty = cr.qty,
                    purpose_type = request_obj.purpose_type,
                    purpose_detail=request_obj.purpose_detail,
                    component=cr.component,
                    request_id = request_obj.id,
                    serial_numbers = ''.join(('"',cr.component.last_sn,'"')) if cr.component.unique_component else serial_numbers,
                    scrap_qty = len(scrap_list),
                    scrap_serial_numbers = scrap_list,
                )) 
            
            Component.objects.filter(pk = cr.component.pk).update(quantity = F('quantity') - cr.qty)

            if not cr.component.unique_component:
                serial_numbers_obj.delete()
            cr.delete()
        if not request_obj.update_status_to_next():
            return Response({"detail": "Cannot update status"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 1: Bulk create the HistoryTrading objects
        created_history = HistoryTrading.objects.bulk_create(history_items)

        # Step 2: Manually create entries in the intermediate table
        relationship_objects = []
        for history in created_history:
            for line in request_obj.lines.all():
                relationship_objects.append(
                    HistoryTrading.lines.through(
                        historytrading_id=history.id,
                        line_id=line.id
                    )
                )
        # Bulk create the relationships in the intermediate table
        HistoryTrading.lines.through.objects.bulk_create(relationship_objects)

        # Cleanup old history and PO records
        HistoryTrading.objects.filter(issue_date__lte = year_expired_date).delete() 
        
        PO.objects.filter(issue_date__lte=year_expired_date).annotate(
            has_serials=Exists(SerialNumber.objects.filter(po=OuterRef('pk')))
        ).filter(has_serials=False).delete()
        
        request_obj.delete()

        return Response({"detail": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_self_pick_up(request):
    try:
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        year_expired_date = now - timedelta(days=2000)

        request_id = request.data.get('request_id')
        emp_name = request.data.get('emp_name')
        serial_numbers_input = request.data.get('serial_numbers')
        sn_list = [item['sn'] for item in serial_numbers_input]

        request_obj = get_object_or_404(Request, id=request_id)

        # Update request as self-pickup
        request_obj.self_pickup = True
        request_obj.save()

        # Update serial numbers
        SerialNumber.objects.filter(serial_number__in=sn_list).update(request=request_obj)

        # Prepare history items
        history_items = []
        component_relate = RequestComponentRelation.objects.filter(request=request_obj)

        for cr in component_relate:
            serial_numbers_obj = SerialNumber.objects.filter(request=request_obj, component=cr.component)
            serial_numbers = [sn.serial_number for sn in serial_numbers_obj]

            request_name = (
                f"{request_obj.requester_emp_center}, {request_obj.requester_name_center} ({request_obj.requester.username})"
                if request_obj.requester_name_center
                else f"{request_obj.requester.emp_id}, {request_obj.requester.username}"
            )

            scrap_qty, scrap_serial_numbers = (0, [])
            if request_obj.scrap_list and not cr.component.unique_component:
                scrap_data = ast.literal_eval(request_obj.scrap_list)
                scrap_qty = len(scrap_data)
                scrap_serial_numbers = [sc['sn'] for sc in scrap_data]

            history_items.append(
                HistoryTrading(
                    requester=request_name,
                    request_date=request_obj.issue_date,
                    staff_approved=request_obj.staff_approved.username,
                    supervisor_approved=request_obj.supervisor_approved.username,
                    trader=emp_name,
                    left_qty=(cr.component.quantity - cr.qty),
                    gr_qty=0,
                    gi_qty=cr.qty,
                    scrap_qty=scrap_qty,
                    purpose_type=request_obj.purpose_type,
                    purpose_detail=request_obj.purpose_detail,
                    component=cr.component,
                    request_id=request_obj.id,
                    serial_numbers=serial_numbers,
                    scrap_serial_numbers=scrap_serial_numbers,
                )
            )

            # Update component quantity
            Component.objects.filter(pk=cr.component.pk).update(quantity=F('quantity') - cr.qty)

            if not cr.component.unique_component:
                serial_numbers_obj.delete()

        # Step 1: Bulk create the HistoryTrading objects
        created_history = HistoryTrading.objects.bulk_create(history_items)

        # Cleanup old history and PO records
        HistoryTrading.objects.filter(issue_date__lte=year_expired_date).delete()

        PO.objects.filter(issue_date__lte=year_expired_date).annotate(
            has_serials=Exists(SerialNumber.objects.filter(po=OuterRef('pk')))
        ).filter(has_serials=False).delete()


        # Step 2: Manually create entries in the intermediate table
        relationship_objects = []
        try:
            for history in created_history:
                for line in request_obj.lines.all():
                    # print('relationship_objects >>>>>>', history.id, line.id)
                    relationship_objects.append(
                        HistoryTrading.lines.through(
                            historytrading_id=history.id,
                            line_id=line.id
                        )
                    )
            # Bulk create the relationships in the intermediate table
            HistoryTrading.lines.through.objects.bulk_create(relationship_objects)

        except Exception as e:
            print(str(e))
            return Response({"detail": f"Error: {str(e)}, {created_history}, {relationship_objects}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)