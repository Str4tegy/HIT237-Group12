from django.contrib import admin

from animals_proj.moderation.models import Flag


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reporter', 'decision', 'created_at', 'reviewed', 'reviewed_by')
    list_filter = ('reviewed', 'decision')
    search_fields = ('reporter__username', 'submission__id')
