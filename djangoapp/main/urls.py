from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('storage/list/', component_list , name='component_list'),
    path('basic_info/list/', basic_info , name='basic_info'),
    path('component/add/', add_component , name='add_component'),
    path('component/update/<int:pk>/', update_component , name='update_component'),
    path('component/delete/<int:pk>/', delete_component , name='delete_component'),
    path('component/list/information/', info_component_list , name='info_component_list'),
    re_path('login_user/', login_user , name='login_user'),
    re_path('logout_user/', logout_user , name='logout_user'),
    re_path('check_in/', check_in , name='check_in'),
]
