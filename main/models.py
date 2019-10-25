from django.db import models


# Группы товаров
class Group(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name='Группа')
    parent_group = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Корневая группа', null=True,
                                     blank=True)

    # Метод возвращает количество товаров в группе и её подгруппах
    def get_product_count(self):
        # Получаем список товаров в группе
        product_count = Product.objects.filter(group=self).count()

        # Получаем список подгрупп и для каждой запрашиваем количество товаров в ней
        sub_groups = Group.objects.filter(parent_group=self)
        for sub_group in sub_groups:
            product_count += sub_group.get_product_count()

        return product_count

    # Метод возвращает True для корневой группы и False - для всех остальных
    def is_root_group(self):
        return self.parent_group is None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['title']


# Товары
class Product(models.Model):
    title = models.CharField(max_length=50, blank=False, unique=True, verbose_name='Наименование')
    description = models.TextField(max_length=1000, blank=False, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, verbose_name='Цена')
    count = models.PositiveIntegerField(blank=False, verbose_name='Количество')
    state = models.BooleanField(blank=False, verbose_name='Новый', null=False)
    arrival_date = models.DateField(blank=False, verbose_name='Дата поступления')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']
