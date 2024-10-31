from django.contrib import admin
from .models import Offer, LeadWall, OfferWebmaster, Click


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'public_status', 'partner_card', 'lead_price', 'offer_price')
    list_filter = ('status', 'public_status', 'partner_card')
    search_fields = ('name', 'inn', 'partner_card__name')

    # Поля, которые нужно скрыть для не-суперпользователей
    superuser_only_fields = ('offer_price', 'validation_data_lead',)  # замените на нужные поля

    def get_fields(self, request, obj=None):
        # Получаем список полей
        fields = super().get_fields(request, obj)
        # Если пользователь не является суперпользователем, удаляем нужные поля
        if not request.user.is_superuser:
            fields = [field for field in fields if field not in self.superuser_only_fields]
        return fields

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    def save_model(self, request, obj, form, change):

        if obj.lead_price > obj.offer_price:
            raise ValueError("Ошибка.")

        if obj.public_status == 'closed' and not obj.lead_price:
            raise ValueError("Необходимо указать цену за лид для закрытого оффера.")

        super().save_model(request, obj, form, change)


@admin.register(LeadWall)
class LeadWallAdmin(admin.ModelAdmin):
    list_display = ('name', 'processing_status', 'status', 'get_offer_name')
    list_filter = ('processing_status', 'status', 'offer_webmaster__offer__name')
    search_fields = ('name', 'description', 'offer_webmaster__offer__name')

    def get_offer_name(self, obj):
        return obj.offer_webmaster.offer.name
    get_offer_name.short_description = 'Оффер'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if not request.user.is_superuser:
            # Ограничить изменение полей, кроме администратора
            readonly_fields += ('processing_status',)
        return readonly_fields

@admin.register(OfferWebmaster)
class OfferWebmasterAdmin(admin.ModelAdmin):
    list_display = ('offer', 'webmaster', 'unique_token', 'phone')
    search_fields = ('offer__name', 'webmaster__name', 'unique_token')

@admin.register(Click)
class OfferClickAdmin(admin.ModelAdmin):
    list_display = ('offer_webmaster', 'created_at')