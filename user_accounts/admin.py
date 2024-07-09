from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomAdminUser, Advertiser, Webmaster

@admin.register(CustomAdminUser)
class CustomAdminUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'telegram', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'telegram', 'phone')}),
    )
    list_display = ('username', 'email', 'role', 'telegram', 'phone', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'role', 'telegram', 'phone')
    list_filter = ('role', 'is_staff', 'is_active')

    class Meta:
        verbose_name = 'Административный пользователь'
        verbose_name_plural = 'Административные пользователи'

@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('email', 'telegram', 'phone')
    search_fields = ('email', 'telegram', 'phone')

    class Meta:
        verbose_name = 'Рекламодатель'
        verbose_name_plural = 'Рекламодатели'

@admin.register(Webmaster)
class WebmasterAdmin(admin.ModelAdmin):
    list_display = ('email', 'telegram', 'phone', 'experience')
    search_fields = ('email', 'telegram', 'phone', 'experience')

    class Meta:
        verbose_name = 'Вебмастер'
        verbose_name_plural = 'Вебмастера'
