from django.urls import path, path
from .views import *

urlpatterns = [
    path('login_user/', login_user , name='login_user'),
    path('logout_user/', logout_user , name='logout_user'),
    path('trading/check_in/', check_in , name='check_in'),

    path('account/pd/area/', get_production_area , name='get_production_area'),
    path('approved/route/info/', get_approved_route , name='get_approved_route'),    

    path('basic_info/list/', basic_info , name='basic_info'),
    path('storage/list/', component_list , name='component_list'),
    path('storage/list/filter/', component_filter , name='component_filter'),
    path('storage/item/info/', component_get_one , name='component_get_one'),

    path('component/info/cart/', component_cart , name='component_cart'),
    path('checkout/cart/', checkout_cart , name='checkout_cart'),

    path('my/request/', my_request , name='my_request'),
    path('my/request/delete/', delete_my_request , name='delete_my_request'),

    path('request/approval/list/', approval_list , name='approval_list'),
    path('request/approved/', approved_order , name='approved_order'),
    path('preparing/list/', preparing_list , name='preparing_list'),
    
    path('component/unique/id/', check_unique_id , name='check_unique_id'),
    path('generate/item/sn/', generate_serial_number , name='generate_serial_number'),
    path('check/item/sn/', check_serial_number_list , name='check_serial_number_list'),



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
