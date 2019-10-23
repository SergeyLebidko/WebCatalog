from django.contrib import admin
from .models import Group, Product


class GroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent_group']
    list_display_links = ['title']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'count', 'state', 'arrival_date']
    list_display_links = ['title', 'description']


admin.site.register(Group, GroupAdmin)
admin.site.register(Product, ProductAdmin)
