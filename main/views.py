from django.shortcuts import render
from django.views.generic.edit import FormView
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy
from .models import Group, Product
from .forms import ProductForm


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
        context['selected_group'] = selected_group
    else:
        context['selected_group'] = None

    return render(request, 'main/products_list.html', context)


# Класс-контроллер для добавления продуктов в базу
class ProductCreator(FormView):
    form_class = ProductForm
    template_name = 'main/create_product.html'
    success_url = reverse_lazy('products_list')

    def get(self, request, *args, **kwargs):
        if 'group_id' not in request.GET or request.GET['group_id'] == 'None':
            return HttpResponseBadRequest()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        new_product = form.save(commit=False)
        group_id = self.request.GET['group_id']
        try:
            selected_group = Group.objects.get(pk=group_id)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            return HttpResponseBadRequest()
        new_product.group = selected_group
        new_product.save()
        return super().form_valid(form)
