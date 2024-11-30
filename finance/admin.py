from django.contrib import admin
from .models import Payments

# Register your models here.
@admin.register(Payments)
class LeadWallAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_type', 'status', 'count')