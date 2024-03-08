from django.urls import path, path
from .views import *

urlpatterns = [
    path('login_user/', login_user , name='login_user'),
    path('logout_user/', logout_user , name='logout_user'),
    path('check_in/', check_in , name='check_in'),

    path('storage/list/', component_list , name='component_list'),
    path('storage/list/filter/', component_filter , name='component_filter'),
    path('basic_info/list/', basic_info , name='basic_info'),

    path('component/add/', add_component , name='add_component'),
    path('component/update/<int:pk>/', update_component , name='update_component'),
    path('component/delete/<int:pk>/', delete_component , name='delete_component'),
    path('component/list/information/', info_component_list , name='info_component_list'),
    path('add/item/serial_number/', add_item , name='add_item'),
    path('serial_number/list/', get_item , name='get_item'),


    path('component/pick_up/', pick_up , name='pick_up'),
    path('component/get_history/', get_history , name='check_in'),
    
    path('account/list/', get_account , name='get_account'),
    path('account/role/update/', set_account_role , name='set_account_role'),
    path('account/delete/', delete_account , name='delete_account'),

    path('add/po/number/', add_po, name='add_po'),
    path('check/po/number/', check_po, name='check_po'),
    
]
