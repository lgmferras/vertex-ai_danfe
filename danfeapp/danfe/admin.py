from django.contrib import admin
from .models import Danfe

# Register your models here.
@admin.register(Danfe)
class DanfeAdmin(admin.ModelAdmin):
    list_display = ('id', 'arquivo_pdf', 'slug', 'created_at',)
    list_display_links = ('arquivo_pdf',)
    search_fields = ('id', 'arquivo_pdf', 'slug')
    list_per_page = 10
    ordering = '-id',
    prepopulated_fields = {'slug': ('arquivo_pdf',)}