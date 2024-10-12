from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import PartnerCard
from offers.models import Offer


@admin.register(PartnerCard)
class PartnerCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'advertiser', 'main_phone', 'deposit', 'is_approved')
    search_fields = ('name', 'legal_name', 'advertiser__user__email')
    list_filter = ('advertiser', 'is_approved')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('deposit',)
        return self.readonly_fields

