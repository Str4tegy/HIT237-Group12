"""
accounts/admin.py  /  species/admin.py  /  submissions/admin.py

Django admin registrations — all in one file here for Pana's reference.
In the actual project these live in each app's admin.py.

Pana's responsibility:
  - Register all models with sensible list_display, search_fields, filters
  - Inline admins for related models (flags inline on submissions)
"""

# ======================================================================
# accounts/admin.py
# ======================================================================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("NT Fauna Profile", {"fields": ("role", "bio", "organisation")}),
    )
    list_display = ["username", "email", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["username", "email", "organisation"]


# ======================================================================
# species/admin.py
# ======================================================================
from species.models import Species, TaxonomicClass


@admin.register(TaxonomicClass)
class TaxonomicClassAdmin(admin.ModelAdmin):
    list_display = ["name", "common_name"]
    search_fields = ["name", "common_name"]


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = [
        "common_name",
        "scientific_name",
        "taxonomic_class",
        "conservation_status",
        "origin",
        "is_threatened",
    ]
    list_filter = ["taxonomic_class", "conservation_status", "origin"]
    search_fields = ["common_name", "scientific_name", "family"]
    readonly_fields = ["created_at", "updated_at", "coordinates_display"]

    @admin.display(boolean=True, description="Threatened?")
    def is_threatened(self, obj):
        return obj.is_threatened


# ======================================================================
# submissions/admin.py
# ======================================================================
from submissions.models import AudioSubmission, SubmissionFlag


class SubmissionFlagInline(admin.TabularInline):
    model = SubmissionFlag
    extra = 0
    readonly_fields = ["reporter", "reason", "created_at", "status"]
    fields = ["reporter", "reason", "status", "notes", "created_at"]


@admin.register(AudioSubmission)
class AudioSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "species",
        "submitter",
        "captured_at",
        "confidence_score",
        "confidence_label",
        "is_flagged",
        "is_visible",
        "created_at",
    ]
    list_filter = ["is_visible", "species__taxonomic_class", "species"]
    search_fields = ["submitter__username", "species__common_name", "location_notes"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "coordinates_display",
        "confidence_label",
        "is_flagged",
    ]
    inlines = [SubmissionFlagInline]

    @admin.display(boolean=True, description="Flagged?")
    def is_flagged(self, obj):
        return obj.is_flagged


@admin.register(SubmissionFlag)
class SubmissionFlagAdmin(admin.ModelAdmin):
    list_display = [
        "submission",
        "reporter",
        "reason",
        "status",
        "reviewed_by",
        "created_at",
    ]
    list_filter = ["status", "reason"]
    search_fields = ["submission__species__common_name", "reporter__username"]
    readonly_fields = ["created_at", "updated_at"]
