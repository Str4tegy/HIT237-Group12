from django.contrib import admin
from submissions.models import AudioSubmission, SubmissionFlag

class SubmissionFlagInline(admin.TabularInline):
    model = SubmissionFlag
    extra = 0
    readonly_fields = ["reporter", "reason", "created_at", "status"]
    fields = ["reporter", "reason", "status", "notes", "created_at"]

@admin.register(AudioSubmission)
class AudioSubmissionAdmin(admin.ModelAdmin):
    list_display = ["species", "submitter", "captured_at", "confidence_score", "is_visible", "created_at"]
    list_filter = ["is_visible", "species__taxonomic_class", "species"]
    search_fields = ["submitter__username", "species__common_name", "location_notes"]
    readonly_fields = ["created_at", "updated_at", "coordinates_display", "confidence_label", "is_flagged"]
    inlines = [SubmissionFlagInline]

@admin.register(SubmissionFlag)
class SubmissionFlagAdmin(admin.ModelAdmin):
    list_display = ["submission", "reporter", "reason", "status", "reviewed_by", "created_at"]
    list_filter = ["status", "reason"]
    search_fields = ["submission__species__common_name", "reporter__username"]
    readonly_fields = ["created_at", "updated_at"]
