from django.contrib import admin

from src.apps.pdf_processing.models import File


class FileAdmin(admin.ModelAdmin):
    list_display = ['file', 'time_add']


admin.site.register(File, FileAdmin)