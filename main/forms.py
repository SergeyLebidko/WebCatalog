from django import forms
from .models import Product


# Форма добавления нового продукта
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'count', 'state', 'arrival_date']
