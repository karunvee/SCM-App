from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *

import time
import ldap3

@api_view(['POST'])
def login_user(request):
    try:
        query_serializer = LoginQuerySerializer(data = request.query_params)
    
        if query_serializer.is_valid():
            username = query_serializer.validated_data.get('username')
            password = query_serializer.validated_data.get('password')
            ad_server = query_serializer.validated_data.get('ad_server')

            if not Member.objects.filter(username = username).exists():
                try:
                    server = ldap3.Server(ad_server, get_info=ldap3.ALL)
                    connect = ldap3.Connection(server, user = username, password = password, auto_bind=True)
                    if connect.bind():
                        user_account = username
                        base_dn = 'DC=delta,DC=corp'  # Update this to your AD's base DN
                        search_filter = f'(sAMAccountName={user_account})'
                        attributes = ['sAMAccountName', 'displayName', 'mail', 'department', 'postalCode']
                        connect.search(search_base=base_dn, search_filter=search_filter, attributes=attributes)

                        if connect.entries:
                            entry = connect.entries[0]
                            print("Account Information:")
                            ad_username = entry.sAMAccountName.value
                            ad_displayName = entry.displayName.value
                            ad_email = entry.mail.value
                            ad_department = entry.department.value
                            ad_employeeId = entry.postalCode.value

                            new_member = Member.objects.create(
                                emp_id = ad_employeeId,
                                username = username,
                                name = "%s" % (ad_displayName),
                                email = ad_email,
                                department = ad_department,

                                is_staff = False,
                                is_user = True,
                                is_superuser = False
                                )

                            serializer = MemberSerializer(new_member)
                            return Response({"detail": f"Successfully added {ad_displayName}.", "data": serializer.data}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"detail": "Failure, This user not found in Active Directory"}, status=status.HTTP_404_NOT_FOUND)
                    
                except Exception as e:
                    return Response({"detail": "Credentials are invalid. please check your username or password."}, status=status.HTTP_404_NOT_FOUND)

            else:
                user = get_object_or_404(Member, username= username)
                if user.is_superuser:
                    if not user.check_password(password):
                        return Response({"detail": "username or password is incorrect."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    e_code, e_msg, valid = validate_credentials(username, ad_server, password)
                    if not valid:
                        return Response({"detail": "Credentials are invalid. please check your username or password."})
                token, create = Token.objects.get_or_create(user=user)
                serializer = MemberSerializer(instance=user)
                return Response({"detail": "success", "token": token.key, "data": serializer.data})
            
        else:
            return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        token_key = request.headers.get('Authorization').split(' ')[1]
        if not token_key:
            return Response({"detail": "Token not provided (%s)" % token_key}, status=status.HTTP_400_BAD_REQUEST)
        token = get_object_or_404(Token, key=token_key)
        token.delete()
        return Response({"detail": "You were logged out."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def check_in(request):
    query_serializer = CheckInQuerySerializer(data = request.query_params)

    if query_serializer.is_valid():
        emp_id = query_serializer.validated_data.get('emp_id')
        user = Member.objects.filter(emp_id = emp_id)
        if user.exists():
            serializer = MemberSerializer(user.get())
            return Response({"detail": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"detail": "This employee id not found"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"detail": "Data format is invalid"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def component_list(request):
    component_list = Component.objects.all()
    serializers = ComponentSerializer(instance=component_list, many=True)
    context = {
        'component_list': serializers.data
    }
    time.sleep(1)
    return Response(context)

@api_view(['GET'])
def basic_info(request):
    ct_serializers = ComponentTypeSerializer(instance=ComponentType.objects.all(), many=True)
    d_serializers = DepartmentSerializer(instance=Department.objects.all(), many=True)
    l_serializers = LocationSerializer(instance=Location.objects.all(), many=True)
    context = {
        'component_type_list': ct_serializers.data,
        'department_list': d_serializers.data,
        'location_list': l_serializers.data
    }
    return Response(context)


@api_view(['POST'])
def add_component(request):
    try:
        print(request.data)
        image = request.data.get('image')
        name = request.data.get('name')
        model = request.data.get('model')
        description = request.data.get('description')
        serial_numbers = request.data.get('serial_numbers').split(',')
        print(serial_numbers)
        component_type, ct_created = ComponentType.objects.get_or_create(name=request.data.get('component_type'), defaults={})
        department, d_created = Department.objects.get_or_create(name=request.data.get('department'), defaults={})
        location, l_created = Location.objects.get_or_create(name=request.data.get('location'), defaults={})
        quantity = request.data.get('quantity')
        quantity_warning = request.data.get('quantity_warning')
        quantity_alert = request.data.get('quantity_alert')

        if not Component.objects.filter(name=name, model=model, department__name=request.data.get('department')).exists():
            component_obj = Component.objects.create(
            image=image,
            name=name,
            model=model,
            description=description,
            component_type=component_type,
            department=department,
            location=location,
            quantity=quantity,
            quantity_warning=quantity_warning,
            quantity_alert=quantity_alert,
            )
            serial_container = []
            for sn in serial_numbers:
                serial_container.append(SerialNumber(serial_number=sn, component=component_obj))
            SerialNumber.objects.bulk_create(serial_container)

            serializer = ComponentSerializer(component_obj)
            return Response({"detail": f"Successfully added {name}.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Failure, duplicate data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        component_obj = component_obj.first()
        image = request.data['image']
        name = request.data['name']
        model = request.data['model']
        serial_numbers = request.data['serial_numbers'].split(',')
        description = request.data['description']
        component_type, ct_created = ComponentType.objects.get_or_create(name = request.data['component_type'], defaults={})
        department, d_created = Department.objects.get_or_create(name = request.data['department'], defaults={})
        location, l_created = Location.objects.get_or_create(name = request.data['location'], defaults={})
        quantity = request.data['quantity']
        quantity_warning = request.data['quantity_warning']
        quantity_alert = request.data['quantity_alert']

        print(serial_numbers)
        if image:
            component_obj.image = image
            component_obj.save()

        # Update other fields
        component_obj.name = name
        component_obj.model = model
        component_obj.description = description
        component_obj.component_type = component_type
        component_obj.department = department
        component_obj.location = location
        component_obj.quantity = quantity
        component_obj.quantity_warning = quantity_warning
        component_obj.quantity_alert = quantity_alert


        serial_container = []
        SerialNumber.objects.filter(component=component_obj).exclude(serial_number__in=serial_numbers).delete()

        for sn in serial_numbers:
            if not SerialNumber.objects.filter(serial_number=sn, component=component_obj).exists():
                serial_container.append(SerialNumber(serial_number=sn, component=component_obj))

        SerialNumber.objects.bulk_create(serial_container)

        component_obj.save()

        return Response({"detail": "%s was update." % name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def delete_component(request, pk):
    component_obj = Component.objects.filter(pk = pk)
    if component_obj.exists():
        component = component_obj.get()
        component.delete()
        return Response({"detail": "%s was deleted." % component.name}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "This data doesn't contain in the database"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def info_component_list(request):
    try:
        serial_numbers = request.data.get('serial_numbers', [])
        print(serial_numbers)
        if not serial_numbers :
            return Response({"detail": "No serial numbers provided"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []
        for sn in serial_numbers:
            if SerialNumber.objects.filter(serial_number=sn).exists():
                components = SerialNumber.objects.get(serial_number=sn)
                component_data = SerialNumberWithComponentSerializer(components).data
            else:
                component_data = {
                    'id': None,
                    'component': None,
                    'serial_number': sn
                }
            response_data.append(component_data.copy())
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)
        return Response({"detail": "Failure, data as your provided is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def pick_up(request):
    emp_id = request.data.get('image')
    serial_numbers = request.data.get('serial_numbers', [])




def validate_credentials(username, ad_server, password):
    try:
        server = ldap3.Server(ad_server, get_info=ldap3.ALL)
        connect = ldap3.Connection(server, user=username, password=password, auto_bind=True)
        if connect.bind():
            return "", "", True
        else:
            print(f"An error occurred: {e}")
            return "1326", 'The user name or password is incorrect.', False
    except Exception as e:
        print(f"An error occurred: {e}")
        return "1326", 'The user name or password is incorrect.', False