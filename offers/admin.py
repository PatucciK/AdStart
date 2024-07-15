from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'public_status', 'partner_card', 'lead_price')
    list_filter = ('status', 'public_status', 'partner_card')
    search_fields = ('name', 'legal_name', 'partner_card__name')
    readonly_fields = ('partner_card',)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('lead_price',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.public_status == 'closed' and not obj.lead_price:
            raise ValueError("Необходимо указать цену за лид для закрытого оффера.")
        super().save_model(request, obj, form, change)
