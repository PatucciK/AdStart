from django.contrib import admin
from .models import Category, Partner


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_private')
    search_fields = ('name',)
    list_filter = ('is_private',)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'official_website', 'phone', 'deposit', 'admin_user', 'advertiser_user')
    search_fields = (
    'name', 'legal_name', 'official_website', 'phone', 'admin_user__username', 'advertiser_user__email')
    list_filter = ('admin_user', 'advertiser_user', 'deposit')

    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'
