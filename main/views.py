from django.shortcuts import render
from .models import Group, Product


# Функция выводит главную страницу
def products_list(request):
    # Получаем выбранную группу
    if 'group_id' in request.GET:
        group_id = request.GET['group_id']
        try:
            selected_group = Group.objects.get(pk=group_id)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            selected_group = None
    else:
        selected_group = None

    # Получаем список продуктов выбранной группы. Если группа не выбрана - получаем полный список продуктов из базы
    if selected_group is not None:
        products = Product.objects.filter(group=selected_group)
    else:
        products = Product.objects.all()

    # Формируем контекст страницы
    context = {'products': products}
    if selected_group is not None:
        context['group_name'] = selected_group.title
    else:
        context['group_name'] = 'все категории'

    return render(request, 'main/index.html', context)
