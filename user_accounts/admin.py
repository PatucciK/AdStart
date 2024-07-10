# user_accounts/admin.py
from django.contrib import admin
from .models import Advertiser, Webmaster


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


admin.site.register(Advertiser, AdvertiserAdmin)
admin.site.register(Webmaster, WebmasterAdmin)
