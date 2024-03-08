from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path('login_user/', login_user , name='login_user'),
    re_path('logout_user/', logout_user , name='logout_user'),
    re_path('check_in/', check_in , name='check_in'),

    re_path('storage/list/', component_list , name='component_list'),
    re_path('basic_info/list/', basic_info , name='basic_info'),

    re_path('component/add/', add_component , name='add_component'),
    path('component/update/<int:pk>/', update_component , name='update_component'),
    path('component/delete/<int:pk>/', delete_component , name='delete_component'),
    re_path('component/list/information/', info_component_list , name='info_component_list'),
    path('add/item/serial_number/', add_item , name='add_item'),
    path('serial_number/list/', get_item , name='get_item'),


    re_path('component/pick_up/', pick_up , name='pick_up'),
    re_path('component/get_history/', get_history , name='check_in'),
    
    re_path('account/list/', get_account , name='get_account'),
    re_path('account/role/update/', set_account_role , name='set_account_role'),
    path('account/delete/', delete_account , name='delete_account'),

    path('add/po/number/', add_po, name='add_po'),
    path('check/po/number/', check_po, name='check_po'),
    
]
