from django.contrib import admin
from .models import Offer, LeadWall, OfferWebmaster, Click, ChangeRequest
from django.db.models import Q
from django.apps import apps

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'public_status', 'partner_card', 'lead_price', 'offer_price')
    list_filter = ('status', 'public_status', 'partner_card')
    search_fields = ('name__icontains', 'inn', 'partner_card__name')

    # Поля, которые нужно скрыть для не-суперпользователей
    superuser_only_fields = ('offer_price', 'validation_data_lead',)  # замените на нужные поля

    def get_fields(self, request, obj=None):
        # Получаем список полей
        fields = super().get_fields(request, obj)
        # Если пользователь не является суперпользователем, удаляем нужные поля
        if not request.user.is_superuser:
            fields = [field for field in fields if field not in self.superuser_only_fields]
        return fields

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(inn__icontains=search_term) |
                Q(partner_card__name__icontains=search_term)
            )
        return queryset, use_distinct


    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('offers.change_lead_price'):
            return ['lead_price']
        return []

    def save_model(self, request, obj, form, change):

        if obj.public_status == 'closed' and not obj.lead_price:
            raise ValueError("Необходимо указать цену за лид для закрытого оффера.")

        if change:
            if request.user.has_perm('offers.change_lead_price'):
                old_obj = self.model.objects.get(pk=obj.pk)  # Получаем старую версию объекта
                old_value = getattr(old_obj, 'lead_price')
                # Вместо сохранения объекта создаем запрос на изменение
                if old_value != obj.lead_price:
                    ChangeRequest.objects.create(
                        user=request.user,
                        target_object_id=obj.id,
                        target_model='Offer',
                        field_name='lead_price',
                        current_value=old_value,
                        requested_value=obj.lead_price
                    )
                else:
                    super().save_model(request, obj, form, change)

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_model', 'field_name', 'current_value', 'requested_value', 'created_at')
    actions = ['approve_changes']

    def approve_changes(self, request, queryset):
        for change_request in queryset:
            # Применение изменений к целевой модели
            model = apps.get_model(app_label='offers', model_name=change_request.target_model)
            obj = model.objects.get(id=change_request.target_object_id)
            obj.lead_price = change_request.requested_value
            obj.save()
            # Отмечаем запрос как одобренный
            change_request.approved = True
            change_request.save()

    approve_changes.short_description = "Approve selected change requests"

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