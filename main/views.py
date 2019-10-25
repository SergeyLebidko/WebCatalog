from django.shortcuts import render
from django.views.generic.edit import FormView
from django.http import HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from .models import Group, Product
from .forms import ProductForm


# Контроллер выводит страницу со списком товаров
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
        context['selected_group'] = selected_group
    else:
        context['selected_group'] = None

    return render(request, 'main/products_list.html', context)


# Контроллер для работы со списком групп
def groups_list(request):
    # Если контроллеру не передан номер группы, то будет выведена информация о корневой группе
    if 'group_id' not in request.GET:
        current_group = Group.objects.get(parent_group=None)
    else:
        try:
            # Если контроллеру передан некорректный номер группы, то возвращается ошибка 400
            current_group = Group.objects.get(pk=request.GET['group_id'])
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            return HttpResponseBadRequest()

    # Получаем список подгрупп выбранной группы
    sub_groups = Group.objects.filter(parent_group=current_group)

    # Получаем группу корневую для текущей
    root_group = current_group.parent_group

    context = {'current_group': current_group, 'sub_groups': sub_groups, 'root_group': root_group}
    return render(request, 'main/groups_list.html', context)


# Класс-контроллер для добавления продуктов в базу
class ProductCreator(FormView):
    form_class = ProductForm
    template_name = 'main/create_product.html'
    success_url = reverse_lazy('products_list')

    def get(self, request, *args, **kwargs):
        if 'group_id' not in request.GET or request.GET['group_id'] == 'None':
            return HttpResponseBadRequest()
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        url = super().get_success_url()+'?group_id='+str(self.group_id)
        return url

    def form_valid(self, form):
        new_product = form.save(commit=False)
        group_id = self.request.GET['group_id']
        try:
            selected_group = Group.objects.get(pk=group_id)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            return HttpResponseBadRequest()
        new_product.group = selected_group
        new_product.save()
        self.group_id = group_id
        return super().form_valid(form)
