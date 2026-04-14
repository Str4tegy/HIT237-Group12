from animals_proj.accounts.models import Profile


def role_flags(request):
    can_access_moderation = False
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            can_access_moderation = True
        else:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            can_access_moderation = profile.is_moderator
    return {'can_access_moderation': can_access_moderation}
