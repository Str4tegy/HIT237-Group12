from django.contrib import admin
from species.models import Species, TaxonomicClass

@admin.register(TaxonomicClass)
class TaxonomicClassAdmin(admin.ModelAdmin):
    list_display = ["name", "common_name"]
    search_fields = ["name", "common_name"]

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ["common_name", "scientific_name", "taxonomic_class", "conservation_status", "origin"]
    list_filter = ["taxonomic_class", "conservation_status", "origin"]
    search_fields = ["common_name", "scientific_name", "family"]
    readonly_fields = ["created_at", "updated_at", "coordinates_display"]
