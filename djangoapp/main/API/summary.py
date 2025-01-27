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
def data_analysis_summary(request):
    try:
        lines = request.data.get('lines', [])
        locations = request.data.get('locations',[])
        component_types = request.data.get('component_types',[])
        machine_types = request.data.get('machine_types',[])
        equipments = request.data.get('equipments',[])
        date_range = request.data.get('date_range')

        print(machine_types)
        query = Q(lines__line_name__in=lines) &\
                Q(component__machine_type__name__in=machine_types)
                # Q(component__location__name__in=locations)
                # Q(component__name__in=equipments)
                # Q(component__component_type__name__in=component_types)
        
        start_date =  datetime.strptime(date_range['start'], '%m/%d/%Y').date()
        end_date =  datetime.strptime(date_range['end'], '%m/%d/%Y').date()
        print(start_date, end_date)
        if start_date and end_date:
            query &= Q(issue_date__range=(start_date, end_date))

        HistoryTradingObj = HistoryTrading.objects.filter(query)
        serializer_data = HistoryTradingSerializer(instance = HistoryTradingObj, many=True)
        return Response({"detail": "success", "data": serializer_data.data}, status=status.HTTP_200_OK)

    except Exception as e:
        print(str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
    