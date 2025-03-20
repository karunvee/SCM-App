from django.urls import path, path
from .views import *

urlpatterns = [
    path("proxy/", ProxyView.as_view(), name="proxy"),
    path('login_user/', login_user , name='login_user'),
    path('logout_user/', logout_user , name='logout_user'),
    path('trading/check_in/', check_in , name='check_in'),

    path('account/pd/area/', get_production_area , name='get_production_area'),
    path('approved/route/info/', get_approved_route , name='get_approved_route'),    

    path('basic_info/list/<str:pda>/', basic_info , name='basic_info'),
    path('location/add/', add_location , name='add_location'),
    path('location/delete/<str:id>/', delete_location , name='delete_location'),
    path('machine/type/add/', add_machine_type , name='add_machine_type'),
    path('machine/type/delete/<str:id>/', delete_machine_type , name='delete_machine_type'),

    path('storage/list/', component_list , name='component_list'), # without Serial Number List
    path('storage/list/filter/', component_filter , name='component_filter'), # with Serial Number List
    path('storage/item/info/', component_get_one , name='component_get_one'),
    path('equipment/serial_number/search/', component_qrcode_search , name='component_qrcode_search'),


    path('component/info/cart/', component_cart , name='component_cart'),
    path('checkout/cart/', checkout_cart , name='checkout_cart'),

    path('my/request/', my_request , name='my_request'),
    path('my/request/delete/', delete_my_request , name='delete_my_request'),

    path('request/approval/list/', approval_list , name='approval_list'),
    path('request/approved/', approved_order , name='approved_order'),
    path('request/approved/to/', approved_order_byMail , name='approved_order_byMail'),

    path('preparing/list/', preparing_list , name='preparing_list'),
    path('request/list/all/', all_request_list , name='all_request_list'),
    
    path('component/unique/id/', check_unique_id , name='check_unique_id'),
    path('generate/item/sn/', generate_serial_number , name='generate_serial_number'),
    path('check/item/sn/', check_serial_number_list , name='check_serial_number_list'),
    path('my/request/pickup/', pick_up , name='pick_up'),
    path('my/request/scrap/<str:request_id>/', scrap , name='scrap'),

    path('self_pickup/list/<str:emp_id>/', self_pick_up_list , name='self_pick_up_list'),
    path('self/pickup/', set_self_pick_up , name='set_self_pick_up'),


    path('component/add/', add_component , name='add_component'),
    path('component/return/', return_component , name='return_component'),
    path('component/checking/model_exist/<str:model>/', component_model_exist_checking , name='component_model_exist_checking'),
    path('component/update/<int:pk>/', update_component , name='update_component'),
    path('component/delete/<int:pk>/', delete_component , name='delete_component'),
    path('component/list/information/', info_component_list , name='info_component_list'),
    path('add/item/serial_number/', add_item , name='add_item'),
    path('add/item/unique/', add_item_unique , name='add_item_unique'),
    path('serial_number/list/', get_item , name='get_item'),
    
    path('account/list/', get_account , name='get_account'),
    path('account/role/update/', set_account_role , name='set_account_role'),
    path('account/delete/', delete_account , name='delete_account'),


    path('check/po/number/', check_po, name='check_po'),

    path('history/gr/gi/', get_grgi, name='get_grgi'),
    path('po/number/history/', get_po, name='get_po'),
    path('po/number/add/', add_po, name='add_po'),
    path('po/number/<str:pn>/', mod_po, name='mod_po'),
    path('po/serial_number/search/', po_qrcode_search , name='po_qrcode_search'),
    path('po/equipment/search/', po_equipment_search , name='po_equipment_search'),

    path('po_relative_component/<str:po_number>/', po_relative_component, name='po_relative_component'),
    path('inventory_list/', inventory_list, name='inventory_list'),
    path('inventory_report_list/<str:day_period>/days/', inventory_report_list, name='inventory_report_list'),
    path('inventory_check/submit/report/', submit_inventory_report, name='submit_inventory_report'),
    
    path('inventory_reset/', inventory_reset, name='inventory_reset'),

    path('location_inventory/<str:day_period>/days/', location_inventory, name='location_inventory'),

    path('proxy/image/pqm/<str:equip_type>/', proxy_image, name='proxy_image'),

    path('lines/list/', get_lines, name='get_lines'),
    path('line/create/', create_line, name='create_line'),
    path('lines/create/bulk/', create_group_lines, name='create_group_lines'),
    path('line/delete/<str:line_name>/', delete_line, name='delete_line'),


    path('data/analysis_summary/', data_analysis_summary, name='data_analysis_summary'),
    path('data/analysis_breakdown/', data_analysis_breakdown, name='data_analysis_breakdown'),

    path('data/machinery_summary/<str:prod_area_name>/', data_machinery_summary, name='data_machinery_summary'),
    

]
