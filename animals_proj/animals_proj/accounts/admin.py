from django.contrib import admin

from animals_proj.accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'affiliation', 'verified')
    list_filter = ('role', 'verified')
    search_fields = ('user__username', 'affiliation')
