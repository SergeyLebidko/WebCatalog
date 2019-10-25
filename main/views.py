from django.shortcuts import render
from django.views.generic.edit import FormView
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from .models import Group, Product
from .forms import GroupForm, ProductForm


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


# Контроллер-функция для редактирования отдельных товаров
def edit_product(request):
    if request.method == 'GET':
        # Пытаемся получить группу, которую будем редактировать
        if 'product_id' in request.GET:
            try:
                edited_product = Product.objects.get(pk=request.GET['product_id'])
            except (Product.DoesNotExist, Product.MultipleObjectsReturned):
                return HttpResponseBadRequest()
        else:
            return HttpResponseBadRequest()

        # Создаем форму для редактирования
        form = ProductForm(instance=edited_product)

        context = {'form': form, 'product_id': request.GET['product_id']}
        return render(request, 'main/edit_product.html', context)

    if request.method == 'POST':
        edited_product = Product.objects.get(pk=request.POST['product_id'])
        form = ProductForm(request.POST, instance=edited_product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('products_list'))
        else:
            return HttpResponseRedirect(reverse('edit_product') + '?product_id=' + request.POST['product_id'])


# Класс-контроллер для добавления товаров в базу
class ProductCreator(FormView):
    form_class = ProductForm
    template_name = 'main/create_product.html'
    success_url = reverse_lazy('products_list')

    def get(self, request, *args, **kwargs):
        if 'group_id' not in request.GET or request.GET['group_id'] == 'None':
            return HttpResponseBadRequest()
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        url = super().get_success_url() + '?group_id=' + str(self.group_id)
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


# Класс-контроллер для добавления групп
class GroupCreator(FormView):
    form_class = GroupForm
    template_name = 'main/create_group.html'
    success_url = reverse_lazy('groups_list')

    def get(self, request, *args, **kwargs):
        if 'root_group_id' not in request.GET:
            return HttpResponseBadRequest()
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        url = super().get_success_url() + '?group_id=' + str(self.root_group_id)
        return url

    def form_valid(self, form):
        new_group = form.save(commit=False)
        root_group_id = self.request.GET['root_group_id']
        try:
            root_group = Group.objects.get(pk=root_group_id)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            return HttpResponseBadRequest()
        new_group.parent_group = root_group
        new_group.save()
        self.root_group_id = root_group_id
        return super().form_valid(form)
