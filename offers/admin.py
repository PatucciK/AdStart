from django.contrib import admin
from .models import Offer, LeadWall


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'public_status', 'partner_card', 'lead_price')
    list_filter = ('status', 'public_status', 'partner_card')
    search_fields = ('name', 'inn', 'partner_card__name')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('lead_price',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.public_status == 'closed' and not obj.lead_price:
            raise ValueError("Необходимо указать цену за лид для закрытого оффера.")
        super().save_model(request, obj, form, change)


@admin.register(LeadWall)
class LeadWallAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'status', 'offer')
    list_filter = ('status', 'offer__name')
    search_fields = ('name', 'phone', 'description', 'offer__name')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if not request.user.is_superuser:
            # Ограничить изменение полей, кроме администратора
            readonly_fields += ('status',)
        return readonly_fields
