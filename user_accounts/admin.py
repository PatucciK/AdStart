# user_accounts/admin.py
from django.contrib import admin
from .models import Advertiser, Webmaster
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User


class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram', 'phone')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


class WebmasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram', 'phone', 'is_approved')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


class CustomUserAdmin(DefaultUserAdmin):
    def get_fieldsets(self, request, obj=None):
        # Получаем стандартные настройки вкладок
        fieldsets = super().get_fieldsets(request, obj)

        # Если пользователь не является суперпользователем, удаляем вкладку "Права доступа"
        if not request.user.is_superuser:
            fieldsets = [
                (name, data)
                for name, data in fieldsets
                if name != 'Права доступа'  # Укажите точное название вкладки "Permissions" для английской версии
            ]
        return fieldsets


admin.site.register(Advertiser, AdvertiserAdmin)
admin.site.register(Webmaster, WebmasterAdmin)

# Перерегистрируем модель User с новым админ-классом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)