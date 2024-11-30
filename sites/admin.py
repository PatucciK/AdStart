import os
import shutil

from django.contrib import admin
from .models import SiteArchive, Category
from django.conf import settings


# Кастомное действие для удаления файлов и записей
@admin.action(description='Удалить выбранные записи и связанные файлы')
def delete_archives_and_files(modeladmin, request, queryset):
    for obj in queryset:
        # Удаление распакованных файлов
        if obj.extracted_path:
            extracted_folder = os.path.join(settings.MEDIA_ROOT, obj.extracted_path)
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder)  # Удалить папку с файлами

        # Удаление самого архива
        if obj.archive:
            if os.path.exists(obj.archive.path):
                os.remove(obj.archive.path)

        # Удаление самого объекта
        obj.delete()

# Register your models here.
@admin.register(SiteArchive)
class SiteArchiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'archive', 'upload_date')
    prepopulated_fields = {'slug': ('name',)}
    actions = [delete_archives_and_files]

    def view_extracted_path(self, obj):
        return format_html(f'<a href="{obj.extracted_path}" target="_blank">{obj.extracted_path}</a>')

    view_extracted_path.short_description = 'Ссылка на распакованные файлы'

@admin.register(Category)
class CategoryArchiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
