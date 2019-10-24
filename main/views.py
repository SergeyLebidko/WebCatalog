from django.shortcuts import render
from .models import Product


# Функция выводит главную страницу
def index(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'main/index.html', context)
