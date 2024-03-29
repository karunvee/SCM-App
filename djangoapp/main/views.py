import json
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import time
import ldap3

from .models import *
from .serializers import *

from .API.component import *
from .API.account import *
from .API.general import *
from .API.cart_request import *
from .API.approved_route import *


@api_view(['POST'])
def login_user(request):
    try:
    
        username = request.data.get('username').lower()
        password = request.data.get('password')
        ad_server = request.data.get('ad_server')

        print(username, password, ad_server)
        if not Member.objects.filter(username = username).exists():

            try:
                server = ldap3.Server(ad_server, get_info=ldap3.ALL)
                connect = ldap3.Connection(server, user = f'DELTA\\{username}', password = password)
                print('hit create new user')

                if connect.bind():

                    user_account = username
                    base_dn = 'DC=delta,DC=corp'  # Update this to your AD's base DN
                    search_filter = f'(sAMAccountName={user_account})'
                    attributes = ['sAMAccountName', 'displayName', 'mail', 'department', 'postalCode']
                    connect.search(search_base=base_dn, search_filter=search_filter, attributes=attributes)

                    if connect.entries:
                        entry = connect.entries[0]

                        ad_username = entry.sAMAccountName.value
                        ad_displayName = entry.displayName.value
                        ad_email = entry.mail.value
                        ad_department = entry.department.value
                        ad_employeeId = entry.postalCode.value
                        print('Hit3')

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

                        token, create = Token.objects.get_or_create(user=new_member)
                        serializer = MemberSerializer(new_member)
                        return Response({"detail": "success", "token": token.key, "data": serializer.data}, status=status.HTTP_201_CREATED)
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
            return Response({"detail": "success", "token": token.key, "data": serializer.data}, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({"detail": f"Failure, data as provided is incorrect. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

def validate_credentials(username, ad_server, password):
    try:
        server = ldap3.Server(ad_server, get_info=ldap3.ALL)
        connect = ldap3.Connection(server, user = f'DELTA\\{username}', password = password)
        print('hit validate_credentials')
        if connect.bind():
            return "", "", True
        else:
            print(f"An error occurred: {e}")
            return "1326", 'The user name or password is incorrect.', False
    except Exception as e:
        print(f"An error occurred: {e}")
        return "1326", 'The user name or password is incorrect.', False
    
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
def basic_info(request):
    ct_serializers = ComponentTypeSerializer(instance=ComponentType.objects.all(), many=True)
    d_serializers = DepartmentSerializer(instance=Department.objects.all(), many=True)
    l_serializers = LocationSerializer(instance=Location.objects.all(), many=True)
    m_serializers = MachineTypeSerializer(instance=MachineType.objects.all(), many=True)
    context = {
        'component_type_list': ct_serializers.data,
        'department_list': d_serializers.data,
        'location_list': l_serializers.data,
        'machine_type_list': m_serializers.data,
    }
    return Response(context)
