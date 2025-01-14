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
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_account(request):
    try:
        members = Member.objects.all().exclude(pk = 1).order_by('-date_joined')
        member_serializer = MemberSerializer(instance=members, many=True)

        return Response({"detail": "success", "data": member_serializer.data}, status=status.HTTP_200_OK)

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
                production_area = pdAreaObj
                )


        members = Member.objects.all().exclude(pk=1)
        member_serializer = MemberSerializer(instance=members, many=True)
        return Response({"detail": "success", "data": member_serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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