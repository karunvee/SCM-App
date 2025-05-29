import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from ..models import *
from ..serializers import *

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_account(request):
    try:
        query_serializer = EmployeeIdQuerySerializer(data = request.query_params)

        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')
            member_req = get_object_or_404(Member, emp_id = emp_id)

            if member_req.is_administrator:
                members = Member.objects.all().exclude(is_superuser=True).order_by('-date_joined')
            else:
                members = Member.objects.filter(Q(production_area=member_req.production_area) | Q(production_area__isnull=True)).exclude(is_superuser=True).order_by('-date_joined')

            member_serializer = MemberSerializer(instance=members, many=True)
            return Response({"detail": "success", "data": member_serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_account_in_production_area(request):
    try:
        query_serializer = ProdAreaNameQuerySerializer(data = request.query_params)

        if query_serializer.is_valid():
            production_area_name = query_serializer.validated_data.get('production_area_name')

            members = Member.objects.filter(production_area__prod_area_name = production_area_name).exclude(is_superuser=True).order_by('name')

            if not members.exists():
                return Response({"detail": "This production area id not found any members.", "data": []}, status=status.HTTP_204_NO_CONTENT)

            member_serializer = MemberSerializer(instance=members, many=True)

            return Response({"detail": "success", "data": member_serializer.data}, status=status.HTTP_200_OK)
            
        
        return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_production_area(request):
    try:
        prodArea = ProductionArea.objects.all()
        serializer = ProductionAreaSerializer(instance=prodArea, many=True)
        return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_account_role(request):
    try:
        update_members = json.loads(request.body.decode('utf-8'))

        for index in update_members:
            
            production_area = index.get('production_area')
            if index.get('production_area') is not None:
                pdAreaObj = get_object_or_404(ProductionArea, pk = production_area.get('id'))
            else:
                continue

            Member.objects.filter(emp_id = index.get('emp_id')).update(
                is_staff = index.get('is_staff'),
                is_supervisor = index.get('is_supervisor'),
                is_center = index.get('is_center'),
                member_role = index.get('member_role'),
                production_area = pdAreaObj
                )


        members = Member.objects.all().exclude(is_superuser=True)
        member_serializer = MemberSerializer(instance=members, many=True)
        return Response({"detail": "success", "data": member_serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_account(request):
    try:
        name = request.data.get('name')
        username = request.data.get('username')
        emp_id = request.data.get('emp_id')
        department = request.data.get('department')
        role = request.data.get('role')
        permission = request.data.get('permission')
        email = request.data.get('email')
        prod_area_name = request.data.get('prod_area_name')
        password = request.data.get('password')
        prod_area = ProductionArea.objects.filter(prod_area_name=prod_area_name).first()

        obj, created = Member.objects.update_or_create(
            emp_id=emp_id,
            username=username,
            defaults={ 
                'name':name,
                'department':department,
                'member_role':role,
                'email':email,
                'production_area': prod_area,
                'is_user': True,
                'is_staff': True if permission == "STAFF" else False,
                'is_local': True
            }
        )
        if created:
            obj.set_password(password)  # Replace with a secure password
            obj.save()
        member_serializer = MemberSerializer(instance=obj)
        return Response({"detail": "success", "data": member_serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    query_serializer = EmployeeIdQuerySerializer(data = request.query_params)

    if query_serializer.is_valid():
        emp_id = query_serializer.validated_data.get('emp_id')

        member = Member.objects.filter(emp_id = emp_id)
        if member.exists():
            member.delete()
            return Response({"detail": "success"}, status=status.HTTP_200_OK)
        
        return Response({"detail": "This employee id not found"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)