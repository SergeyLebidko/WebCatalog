from django import forms
from .models import Group, Product


# Форма добавления новой группы
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title']


# Форма добавления нового продукта
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'count', 'state', 'arrival_date']
