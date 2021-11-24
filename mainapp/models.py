from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime


class Company(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название компании')
    ur_address = models.CharField(max_length=50, verbose_name='Юридический адрес')
    fys_address = models.CharField(max_length=50, verbose_name='Физический адрес')
    phone = models.CharField(max_length=25, verbose_name='Телефон')
    email = models.EmailField(max_length=30, verbose_name='Email')
    director = models.CharField(max_length=50, verbose_name='Директор')
    inn = models.CharField(max_length=12, verbose_name='ИНН')
    kpp = models.CharField(max_length=9, verbose_name='КПП')
    bill_acc = models.CharField(max_length=20, verbose_name='Расчётный счёт')
    bik = models.CharField(max_length=9, verbose_name='БИК')

    def __str__(self):
        return self.name


STATUS_CHOICES = (
    ('Проектирование', 'Проектирование'),
    ('Дизайн', 'Дизайн'),
    ('Разработка', 'Разработка'),
    ('Верстка', 'Верстка'),
    ('Согласование', 'Согласование'),
)


class Posts(models.Model):
    id = models.AutoField
    post_name = models.CharField(max_length=50, verbose_name='Название должности')
    department = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Согласование', verbose_name='Отдел')

    def __str__(self):
        return self.post_name


class Employees(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    last_name = models.CharField(max_length=20, verbose_name='Фамилия')
    first_name = models.CharField(max_length=20, verbose_name='Имя')
    up_name = models.CharField(max_length=20, verbose_name='Отчество', null=True)
    post = models.ForeignKey(Posts, verbose_name='Должность', on_delete=models.CASCADE)
    phone = models.CharField(max_length=25, verbose_name='Телефон')
    email = models.EmailField(max_length=30, verbose_name='Email')
    image = models.ImageField(verbose_name='аватар')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Customers(models.Model):
    id = models.AutoField
    name = models.CharField(max_length=50, verbose_name='Организация')
    director = models.CharField(max_length=50, verbose_name='Директор')
    phone = models.CharField(max_length=25, verbose_name='Телефон')
    email = models.EmailField(max_length=30, verbose_name='Email')
    inn = models.CharField(max_length=12, verbose_name='ИНН', validators=[MinLengthValidator(10)])
    kpp = models.CharField(max_length=9, verbose_name='КПП', validators=[MinLengthValidator(9)])
    bill_acc = models.CharField(max_length=20, verbose_name='Расчётный счёт', validators=[MinLengthValidator(20)])
    bik = models.CharField(max_length=9, verbose_name='БИК', validators=[MinLengthValidator(9)])

    def __str__(self):
        return self.name


class Projects(models.Model):
    id = models.AutoField
    name = models.CharField(max_length=50, verbose_name='Название проекта')
    customer_id = models.ForeignKey(Customers, verbose_name='Код заказчика', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', null=True)
    date = models.DateField(auto_now_add=True, verbose_name='Дата заказа')
    deadline = models.DateField(verbose_name='Дата дедлайна')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус выполнения')
    curator = models.ForeignKey(Employees, verbose_name='Код куратора', on_delete=models.PROTECT)
    budget = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Бюджет')
    contract = models.FileField(null=True, verbose_name='Договор')

    def __str__(self):
        return self.name


class Archive(models.Model):
    id = models.AutoField
    name = models.CharField(max_length=50, verbose_name='Название проекта')
    customer_id = models.ForeignKey(Customers, verbose_name='Код заказчика', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, verbose_name='Дата заказа')
    deadline = models.DateField(verbose_name='Дата дедлайна')
    budget = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Бюджет')
    contract = models.FileField(null=True, verbose_name='Договор')
    act = models.FileField(null=True, verbose_name='Акт работ')

    def __str__(self):
        return self.name


class Tasks(models.Model):
    id = models.AutoField
    project_id = models.ForeignKey(Projects, verbose_name='Код проекта', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Наименование услуги')

    def __str__(self):
        return self.name


class Comments(models.Model):
    id = models.AutoField
    project_id = models.ForeignKey(Projects, verbose_name='Код проекта', on_delete=models.CASCADE)
    emp_id = models.ForeignKey(Employees, verbose_name='Код сотрудника', on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='Комментарий')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')

    def __str__(self):
        return self.comment
