from django.urls import path
from .views import *

urlpatterns = [
    path('storage/list/', component_list , name='component_list'),
    path('basic_info/list/', basic_info , name='basic_info'),
    path('component/add/', add_component , name='add_component'),
    path('component/delete/<int:pk>/', delete_component , name='delete_component'),
]
