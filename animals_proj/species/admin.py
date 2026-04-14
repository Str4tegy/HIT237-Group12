from django.contrib import admin
from .models import Species


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'taxon_class', 'conservation_status', 'is_endemic')
    search_fields = ('common_name', 'scientific_name')
    list_filter = ('taxon_class', 'conservation_status', 'is_endemic')
