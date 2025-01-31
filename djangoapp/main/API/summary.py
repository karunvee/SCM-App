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
from dateutil.relativedelta import relativedelta

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
        date_mode = request.data.get('date_mode')
        date_range = request.data.get('date_range')

        query_main = Q(lines__line_name__in=lines) &\
                Q(component__location__name__in=locations) &\
                Q(component__component_type__name__in=component_types) &\
                Q(component__machine_type__name__in=machine_types) # &\
                # Q(component__name__in=equipments)
        
        start_date =  datetime.strptime(date_range['start'], '%m/%d/%Y').date()
        end_date =  datetime.strptime(date_range['end'], '%m/%d/%Y').date()

        date_series = []
        date_labels = []
        labelUpdated = False
        for line in lines:
            series_index = {}
            series_index['name'] = line
            series_index['gi_data'] = []
            series_index['scrap_data'] = []
            series_index['cost_data'] = []

            if date_mode == 'Days':
                current_date = start_date
                while current_date <= end_date:
                    # print(current_date)  # You can replace this with the action you need to perform
                    hObj = HistoryTrading.objects.filter(
                        Q(lines__line_name=line) &\
                        Q(component__location__name__in=locations) &\
                        Q(component__component_type__name__in=component_types) &\
                        Q(component__machine_type__name__in=machine_types) &\
                        Q(issue_date__date=current_date)
                    )
                    gi = 0
                    scrap = 0
                    cost = 0
                    for h in hObj:
                        gi = gi + h.gi_qty
                        scrap = scrap + h.scrap_qty
                        cost = cost + (h.component.price * h.gi_qty)

                    series_index['gi_data'].append(gi)
                    series_index['scrap_data'].append(scrap)
                    series_index['cost_data'].append(cost)

                    if not labelUpdated : date_labels.append(current_date)
                    current_date += timedelta(days=1)

            elif date_mode == 'Months':
                current_date = start_date.replace(day=1)  # Set the day to 1 to avoid inconsistencies
                while current_date <= end_date:
                    print(current_date.month)  # You can replace this with your desired output or action
                    if not labelUpdated : date_labels.append(current_date)

                    query &= Q(date__month=current_date.month)
                    hObj = HistoryTrading.objects.filter(query)

                    series_index['data'].append(current_date)

                    current_date += relativedelta(months=1)  # Move to the next month

            elif date_mode == 'Years':
                current_date = start_date.replace(month=1, day=1)  # Set the date to the 1st of January of the start year
                while current_date <= end_date:
                    print(current_date.year)  # You can replace this with your desired output or action
                    if not labelUpdated : date_labels.append(current_date)
                    series_index['data'].append(current_date)

                    current_date += relativedelta(years=1)  # Move to the next yearate.year, end_date.year + 1): 
            else:
                return Response({"detail": 'date_mode data format is not correct'}, status=status.HTTP_409_CONFLICT)
            
            labelUpdated = True
            date_series.append(series_index)


        data = {}
        data['overall'] = {}
        data['overall']['series'] = date_series
        data['overall']['labels'] = date_labels

        data['cost_total'] = {}
        data['gi_scrap'] = {}

        # for hObj in HistoryTradingObj:




        return Response({"detail": "success", "data": data}, status=status.HTTP_200_OK)

    except Exception as e:
        print(str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
#  overall: {
#                 series: [
#                     {
#                         name: "L1",
#                         data: [10, 41, 35, 51, 49, 62, 69, 91, 148]
#                     },
#                     {
#                         name: "L2",
#                         data: [41, 25, 25, 12, 65, 45, 89, 21, 25]
#                     },
#                     {
#                         name: "L3",
#                         data: [47, 85, 75, 45, 35, 12, 77, 25, 42]
#                     }
#                 ],
#                 labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
#             }    