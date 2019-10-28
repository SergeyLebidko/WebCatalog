from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView
from django.db.models import Min, Max, Count
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
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
    paginator = Paginator(products, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    if not (1 <= int(page_num) <= int(paginator.num_pages)):
        return HttpResponseBadRequest()
    page = paginator.get_page(page_num)
    products = page.object_list

    context = {'products': products, 'page': page}
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


# Контроллер-функция для удаления товаров
def remove_product(request):
    # Получаем удаляемый товар
    if 'product_id' not in request.GET:
        return HttpResponseBadRequest()
    try:
        product = Product.objects.get(pk=request.GET['product_id'])
    except (Product.DoesNotExist, Product.MultipleObjectsReturned):
        return HttpResponseBadRequest()

    # Удаляем товар
    group_id = product.group.pk
    product.delete()

    return HttpResponseRedirect(reverse_lazy('products_list') + '?group_id=' + str(group_id))


# Контроллер-функция удаления группы
def remove_group(request):
    # Получаем удаляемую группу
    if 'group_id' not in request.GET:
        return HttpResponseBadRequest()
    try:
        group = Group.objects.get(pk=request.GET['group_id'])
    except (Group.DoesNotExist, Group.MultipleObjectsReturned):
        return HttpResponseBadRequest()

    # Удаляем группу
    root_group_id = group.parent_group.pk
    group.delete()

    return HttpResponseRedirect(reverse_lazy('groups_list') + '?group_id=' + str(root_group_id))


# Контроллер-функция для формирования страницы статистики
def statistic(request):
    price_stat = Product.objects.aggregate(Min('price'), Max('price'))
    price_min = price_stat['price__min']
    price_max = price_stat['price__max']
    products_with_min_price = Product.objects.filter(price=price_min)
    products_with_max_price = Product.objects.filter(price=price_max)
    avg_price = (price_min + price_max) // 2

    all_products = Product.objects.all()
    products_count = all_products.count()

    total_cost = 0
    for product in all_products:
        total_cost += (product.price * product.count)

    # Пример использования группировки. Получаем количество товаров, поступивших в каждую из дат
    count_products_in_date = Product.objects.values('arrival_date').order_by('-arrival_date').annotate(cnt=Count('pk'))

    context = {
        'price_min': price_min,
        'price_max': price_max,
        'products_with_min_price': products_with_min_price,
        'products_with_max_price': products_with_max_price,
        'avg_price': avg_price,
        'products_count': products_count,
        'total_cost': total_cost,
        'count_products_in_date': count_products_in_date
    }
    return render(request, 'main/statistic.html', context)


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


# Класс-контроллер для редактирования групп
class GroupEditor(UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'main/edit_group.html'
    pk_url_kwarg = 'group_id'

    def get_object(self, queryset=None):
        if 'group_id' not in self.request.GET:
            raise Http404()
        try:
            obj = Group.objects.get(pk=self.request.GET['group_id'])
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            raise Http404()
        # self.object = obj
        return obj

    def get_success_url(self):
        root_group = self.object.parent_group
        if root_group is None:
            return reverse_lazy('groups_list')
        else:
            return reverse_lazy('groups_list') + '?group_id=' + str(root_group.pk)
