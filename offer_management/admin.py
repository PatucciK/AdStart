from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'partner', 'legal_name', 'inn', 'contract_number', 'contract_date', 'official_website', 'lead_price')
    search_fields = ('name', 'status', 'partner__name', 'legal_name', 'inn', 'contract_number', 'official_website')
    list_filter = ('status', 'partner', 'contract_date')

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'
