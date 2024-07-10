from django.contrib import admin
from .models import Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'offer', 'landing_type', 'status', 'path', 'webmaster')
    search_fields = ('name', 'offer__name', 'landing_type', 'status', 'path', 'webmaster__email')
    list_filter = ('landing_type', 'status', 'offer', 'webmaster')

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'
