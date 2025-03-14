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
        date_start = request.data.get('date_start')
        # date_range = request.data.get('date_range')
        # start_date =  datetime.strptime(date_range['start'], '%m/%d/%Y').date()
        # end_date =  datetime.strptime(date_range['end'], '%m/%d/%Y').date()

        
        date_start =  datetime.strptime(date_start, '%m/%d/%Y').date() 

        if date_mode == 'days':
            date_end =  date_start + relativedelta(days=1)

            return Response({"detail": 'This mode is not available to use.', "data": []}, status=status.HTTP_403_FORBIDDEN)
        
        elif date_mode == 'months':
            date_end =  date_start + relativedelta(months=1)
            print(date_start, date_end)

            # hObj = HistoryTrading.objects.filter(
            #     Q(lines__line_name=line_name) &\
            #     Q(component__location__name__in=locations) &\
            #     Q(component__component_type__name__in=component_types) &\
            #     Q(component__machine_type__name__in=machine_types) &\
            #     Q(issue_date__date__range=[date_start, date_end])
            # )
            # print(hObj.values_list('component_id', flat=True))
            # print('*****')
            # components = Component.objects.filter(
            #     id__in=hObj.values_list('component_id', flat=True)

            components = Component.objects.filter(
                historytrading__lines__line_name=line_name,
                historytrading__component__location__name__in=locations,
                historytrading__component__component_type__name__in=component_types,
                historytrading__component__machine_type__name__in=machine_types,
                historytrading__issue_date__range=[date_start, date_end]
            ).annotate(
                total_gi_qty=Coalesce(Sum('historytrading__gi_qty', filter=Q(historytrading__issue_date__date__range=[date_start, date_end])), Value(0)),
                total_scrap_qty=Coalesce(Sum('historytrading__scrap_qty', filter=Q(historytrading__issue_date__date__range=[date_start, date_end])), Value(0)),
                total_price=Coalesce(Sum(F('historytrading__gi_qty') * F('price'), filter=Q(historytrading__issue_date__date__range=[date_start, date_end])), Value(0)),
            )

            data = [
                {
                    "id": component.pk,
                    "name": component.name,
                    "model": component.model,
                    "component_type": component.component_type.name,
                    "machine_type": component.machine_type.name,
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

            return Response({"detail": 'success', "data": data, "date_range": f"{date_start.strftime('%m/%d/%Y')} to {date_end.strftime('%m/%d/%Y')}"}, status=status.HTTP_200_OK)

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
        locations = request.data.get('locations', [])
        component_types = request.data.get('component_types', [])
        machine_types = request.data.get('machine_types', [])
        date_mode = request.data.get('date_mode')
        date_range = request.data.get('date_range')

        start_date = datetime.strptime(date_range['start'], '%m/%d/%Y').date()
        end_date = datetime.strptime(date_range['end'], '%m/%d/%Y').date()

        data_series = []
        date_labels = []
        label_updated = False

        for line in lines:
            series_data = {
                'name': line,
                'gi_data': [],
                'scrap_data': [],
                'cost_data': []
            }

            current_date = start_date
            date_increment = timedelta(days=1) if date_mode == 'Days' else None

            if date_mode == 'Months':
                current_date = start_date.replace(day=1)
                date_increment = relativedelta(months=1)
            elif date_mode == 'Years':
                current_date = start_date.replace(month=1, day=1)
                date_increment = relativedelta(years=1)

            if not date_increment:
                return Response({"detail": 'Invalid date_mode'}, status=status.HTTP_409_CONFLICT)

            while current_date <= end_date:
                date_filter = Q(issue_date__date__range=(start_date, end_date)) if date_mode == 'Days' \
                    else Q(issue_date__month=current_date.month, issue_date__year=current_date.year)

                h_objects = HistoryTrading.objects.filter(
                    Q(lines__line_name=line) &
                    Q(component__location__name__in=locations) &
                    Q(component__component_type__name__in=component_types) &
                    Q(component__machine_type__name__in=machine_types) &
                    date_filter
                )

                gi = sum(h.gi_qty for h in h_objects)
                scrap = sum(h.scrap_qty for h in h_objects)
                cost = sum(h.component.price * h.gi_qty for h in h_objects)

                series_data['gi_data'].append(gi)
                series_data['scrap_data'].append(scrap)
                series_data['cost_data'].append(cost)

                if not label_updated:
                    date_labels.append(current_date.strftime('%m/%d/%Y'))
                
                current_date += date_increment

            label_updated = True
            data_series.append(series_data)

        data = {
            'overall': {'series': data_series, 'labels': date_labels},
            'gi_total': {'series': [], 'labels': []},
            'scrap_total': {'series': [], 'labels': []},
            'cost_total': {'series': [], 'labels': []},
        }

        for series in data_series:
            data['gi_total']['labels'].append(series['name'])
            data['gi_total']['series'].append(sum(series['gi_data']))

            data['scrap_total']['labels'].append(series['name'])
            data['scrap_total']['series'].append(sum(series['scrap_data']))

            data['cost_total']['labels'].append(series['name'])
            data['cost_total']['series'].append(sum(series['cost_data']))

        return Response({"detail": "success", "data": data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
