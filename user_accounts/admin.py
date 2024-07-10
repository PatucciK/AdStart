from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Advertiser, Webmaster


class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'telegram', 'phone')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


class WebmasterAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'telegram', 'phone', 'is_approved')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


admin.site.register(Advertiser, AdvertiserAdmin)
admin.site.register(Webmaster, WebmasterAdmin)
