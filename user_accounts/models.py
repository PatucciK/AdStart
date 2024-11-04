from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


class Advertiser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram',
        help_text='Telegram аккаунт рекламодателя'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text='Телефон рекламодателя'
    )

    about = models.TextField(
        max_length=500,
        blank=True,
        null=False,
        verbose_name='Описание услуги',
        help_text='Описание услуги'
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Рекламодатель'
        verbose_name_plural = 'Рекламодатели'


class Webmaster(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram',
        help_text='Telegram аккаунт вебмастера'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text='Телефон вебмастера'
    )
    experience = models.TextField(
        blank=True,
        null=True,
        verbose_name='Опыт',
        help_text='Опыт вебмастера'
    )
    stats_screenshot = models.ImageField(
        upload_to='screenshots/',
        blank=True,
        null=True,
        verbose_name='Скриншот статистики',
        help_text='Скриншот статистики вебмастера'
    )
    is_approved = models.BooleanField(
        verbose_name="Подтверждение администратором",
        default=False,
        help_text="Подтверждение регистрации вебмастера, для передачи вебмастеру доступа к системе поставьте галочку "
                  "в этом поле и сохраните изменения!"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Баланс', default=0)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Вебмастер'
        verbose_name_plural = 'Вебмастера'


class EmailConfirmation(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    confirmation_code = models.CharField(max_length=6, verbose_name="Код подтверждения")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтверждено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def is_expired(self):
        expiration_time = self.updated_at + timedelta(minutes=10)
        return timezone.now() > expiration_time

    def __str__(self):
        return self.email


