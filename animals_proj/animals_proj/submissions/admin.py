from django.contrib import admin

from animals_proj.submissions.models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'species', 'submitter', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'species')
    search_fields = ('submitter__username', 'species__common_name', 'species__scientific_name')
