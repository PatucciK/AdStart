from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomAdminUser(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('finance', 'Финансы'),
        ('manager', 'Менеджер'),
        ('designer', 'Верстальщик'),
        ('call_center_operator', 'Оператор Колл-центра'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        verbose_name='Роль',
        help_text='Роль пользователя'
    )
    telegram = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram',
        help_text='Telegram аккаунт пользователя'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text='Телефон пользователя'
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customadminuser_set',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customadminuser',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customadminuser_set',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customadminuser',
    )

    class Meta:
        verbose_name = 'Административный пользователь'
        verbose_name_plural = 'Административные пользователи'


class Advertiser(models.Model):
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Email рекламодателя'
    )
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
    password = models.CharField(
        max_length=128,
        verbose_name="Пароль"
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Рекламодатель'
        verbose_name_plural = 'Рекламодатели'


class Webmaster(models.Model):
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Email вебмастера'
    )
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
    password = models.CharField(
        max_length=128,
        verbose_name="Пароль"
    )

    def __str__(self):
        return self.email

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
        # Определите срок действия кода (например, 10 минут)
        expiration_time = self.updated_at + timedelta(minutes=10)
        return timezone.now() > expiration_time


    def __str__(self):
        return self.email
