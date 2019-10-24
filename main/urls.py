from django.urls import path
from .views import *


urlpatterns = [
    path('products_list/', products_list, name='products_list'),
    path('create_product/', ProductCreator.as_view(), name='create_product')
]
