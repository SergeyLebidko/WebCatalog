from django.urls import path
from .views import *

urlpatterns = [
    path('products_list/', products_list, name='products_list')
]