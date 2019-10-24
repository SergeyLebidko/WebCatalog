from django.db import models


# Группы товаров
class Group(models.Model):
    title = models.CharField(max_length=50, verbose_name='Группа')
    parent_group = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Корневая группа', null=True,
                                     blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['title']


# Товары
class Product(models.Model):
    title = models.CharField(max_length=50, blank=False, verbose_name='Наименование')
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
