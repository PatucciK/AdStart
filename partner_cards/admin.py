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
    readonly_fields = ('advertiser',)  # Это будет использоваться для существующих записей

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('deposit',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change and 'is_approved' in form.changed_data and obj.is_approved:
            # Создаем новый оффер при одобрении карточки партнера
            Offer.objects.create(
                partner_card=obj,
                name=f"Оффер #{obj.pk}",
                legal_name=obj.legal_name,
                website=obj.website,
                legal_address=obj.legal_address,
                actual_addresses=obj.actual_addresses,
                working_hours='',
                service_description='Описание услуг по офферу',
                geo='',
                lead_validity='',
                landing_page='',
                postback_documentation='',
                lead_price=0.00
            )

        super().save_model(request, obj, form, change)

        # Редирект на страницу оффера в админке
        if change and 'is_approved' in form.changed_data and obj.is_approved:
            offer = Offer.objects.get(partner_card=obj)
            return HttpResponseRedirect(reverse('admin:offers_offer_change', args=[offer.pk]))
