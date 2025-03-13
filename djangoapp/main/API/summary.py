import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Q, Value
from django.db.models.functions import Coalesce
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
def data_analysis_breakdown(request):
    try:
        line_name = request.data.get('line_name')
        locations = request.data.get('locations',[])
        component_types = request.data.get('component_types',[])
        machine_types = request.data.get('machine_types',[])
        equipments = request.data.get('equipments',[])
        date_mode = request.data.get('date_mode').lower()
        date_range = request.data.get('date_range')

        start_date =  datetime.strptime(date_range['start'], '%m/%d/%Y').date()
        end_date =  datetime.strptime(date_range['end'], '%m/%d/%Y').date()

        if date_mode == 'days':
            return Response({"detail": 'This mode is not available to use.'}, status=status.HTTP_403_FORBIDDEN)
        
        elif date_mode == 'months':

            hObj = HistoryTrading.objects.filter(
                Q(lines__line_name=line_name) &\
                Q(component__location__name__in=locations) &\
                Q(component__component_type__name__in=component_types) &\
                Q(component__machine_type__name__in=machine_types) &\
                Q(issue_date__month__range=[start_date.month, end_date.month])
            )
            print(hObj.values_list('component_id', flat=True))
            print('*****')
            components = Component.objects.filter(
                id__in=hObj.values_list('component_id', flat=True)
            ).annotate(
                total_gi_qty=Coalesce(Sum('historytrading__gi_qty', filter=Q(historytrading__issue_date__date__range=[start_date, end_date])), Value(0)),
                total_scrap_qty=Coalesce(Sum('historytrading__scrap_qty', filter=Q(historytrading__issue_date__date__range=[start_date, end_date])), Value(0)),
                total_price=Coalesce(Sum(F('historytrading__gi_qty') * F('price'), filter=Q(historytrading__issue_date__date__range=[start_date, end_date])), Value(0)),
            )

            data = [
                {
                    "id": component.pk,
                    "name": component.name,
                    "model": component.model,
                    "unique_id": component.unique_id,
                    "price": component.price,
                    "location": component.location.name,
                    "image": component.image_url,
                    "total_gi_qty": component.total_gi_qty,
                    "total_scrap_qty": component.total_scrap_qty,
                    "total_price": component.total_price,
                }
                for component in components
            ]

            return Response({"detail": 'success', "data": data}, status=status.HTTP_200_OK)

        else:
            return Response({"detail": 'date_mode data format is not correct'}, status=status.HTTP_409_CONFLICT)

    except Exception as e:
        print(str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

        data_series = []
        date_labels = []
        labelUpdated = False
        for line in lines:
            series_index = {}
            series_index['name'] = line
            series_index['gi_data'] = []
            series_index['scrap_data'] = []
            series_index['cost_data'] = []
            series_index['data'] = []

            if date_mode == 'Days':
                current_date = start_date
                while current_date <= end_date:

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
                    # print(current_date, end_date)
                    hObj = HistoryTrading.objects.filter(
                        Q(lines__line_name=line) &\
                        Q(component__location__name__in=locations) &\
                        Q(component__component_type__name__in=component_types) &\
                        Q(component__machine_type__name__in=machine_types) &\
                        Q(issue_date__month=current_date.month)
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

                    if not labelUpdated : date_labels.append(datetime.strftime(current_date, '%Y-%m'))
                    current_date += relativedelta(months=1)  # Move to the next month

            elif date_mode == 'Years':
                current_date = start_date.replace(month=1, day=1)  # Set the date to the 1st of January of the start year
                while current_date <= end_date:
                    # print(current_date.year)  # You can replace this with your desired output or action
                    if not labelUpdated : date_labels.append(current_date)
                    series_index['data'].append(current_date)

                    current_date += relativedelta(years=1)  # Move to the next yearate.year, end_date.year + 1): 
            else:
                return Response({"detail": 'date_mode data format is not correct'}, status=status.HTTP_409_CONFLICT)
            
            labelUpdated = True
            data_series.append(series_index)


        data = {}
        data['overall'] = {}
        data['overall']['series'] = data_series
        data['overall']['labels'] = date_labels

        data['gi_total'] = {}
        data['gi_total']["series"] = []
        data['gi_total']["labels"] = []
        data['scrap_total'] = {}
        data['scrap_total']["series"] = []
        data['scrap_total']["labels"] = []
        data['cost_total'] = {}
        data['cost_total']["series"] = []
        data['cost_total']["labels"] = []
        for s in data_series:
            tt_gi_line = 0
            tt_scrap_line = 0
            tt_cost_line = 0

            for gi_line in s["gi_data"]: tt_gi_line += gi_line
            data['gi_total']["labels"].append(s["name"])
            data['gi_total']["series"].append(tt_gi_line)

            for scrap_line in s["scrap_data"]: tt_scrap_line += scrap_line
            data['scrap_total']["labels"].append(s["name"])
            data['scrap_total']["series"].append(tt_scrap_line)

            for cost_line in s["cost_data"]: tt_cost_line += cost_line
            data['cost_total']["labels"].append(s["name"])
            data['cost_total']["series"].append(tt_cost_line)


        return Response({"detail": "success", "data": data}, status=status.HTTP_200_OK)

    except Exception as e:
        print(str(e))
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
