from django.contrib import admin
from .models import Flag


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reporter', 'created_at', 'reviewed')
    list_filter = ('reviewed',)
    search_fields = ('reporter__username', 'submission__id')
