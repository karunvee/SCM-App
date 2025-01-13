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


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_lines(request):
    try:
        query_serializer = EmployeeIdQuerySerializer(data = request.query_params)
        if query_serializer.is_valid():
            emp_id = query_serializer.validated_data.get('emp_id')
            
            memberObj = get_object_or_404(Member, emp_id = emp_id)
            lineObj = Line.objects.filter(production_area = memberObj.production_area)
            serializes = LineSerializer(instance = lineObj, many=True)
            return Response({"detail": "success", "lines" : serializes.data }, status=status.HTTP_200_OK)
        else:
            Response({ "detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST', 'PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_line(request):
    try:
        if request.method == 'POST':
            name = request.data.get('name')
            emp_id = request.data.get('emp_id')

            memberObj = get_object_or_404(Member, emp_id = emp_id)

            c = Line.objects.create(
                name = name,
                production_area = memberObj.production_area
            )
            serializer = LineSerializer(instance = c)
            return Response({ "detail": "success", "created_data": serializer.data}, status=status.HTTP_201_CREATED)
        
        elif request.method == 'PUT':
            id = request.data.get('id')
            name = request.data.get('name')
            Line.objects.filter(id = id).update(name = name)

            return Response({ "detail": "success"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_group_lines(request):
    try:
        createLines = []
        line_list = request.data.get('line_list')
        emp_id = request.data.get('emp_id')

        memberObj = get_object_or_404(Member, emp_id = emp_id)

        for line in line_list:
            createLines.append(
                Line(
                    name = line,
                    production_area = memberObj.production_area
                )
            )
        bLine = Line.objects.bulk_create(createLines)
        serializer = LineSerializer(instance = bLine, many=True)
        return Response({ "detail": "success", "created_data": serializer.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_line(request, line_name):
    try:
        lineObj = get_object_or_404(Line, name = line_name)
        lineObj.delete()
        
        return Response({ "detail": "success"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)