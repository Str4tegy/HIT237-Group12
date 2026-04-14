from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'species', 'submitter', 'status', 'created_at')
    list_filter = ('status', 'species')
    search_fields = ('submitter__username', 'species__common_name', 'species__scientific_name')
