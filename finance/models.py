from django.db import models
from django.contrib.auth.models import User

class Payments(models.Model):
    PAYMENT_TYPE = [
        ('out', 'вывод'),
        ('in', 'ввод')
    ]

    PAYMENT_STATUS = [
        ('in_processing', 'В проссе'),
        ('success', 'Успешно')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE, default='registered', verbose_name='Вид выплаты')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='registered', verbose_name='Статус заявки')
    count = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма выплаты', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

