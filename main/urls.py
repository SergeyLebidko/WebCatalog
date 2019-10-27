from django.urls import path
from .views import *

urlpatterns = [
    path('', products_list),
    path('products_list/', products_list, name='products_list'),
    path('groups_list/', groups_list, name='groups_list'),
    path('create_group/', GroupCreator.as_view(), name='create_group'),
    path('create_product/', ProductCreator.as_view(), name='create_product'),
    path('edit_product/', edit_product, name='edit_product'),
    path('edit_group/', GroupEditor.as_view(), name='edit_group')
]
