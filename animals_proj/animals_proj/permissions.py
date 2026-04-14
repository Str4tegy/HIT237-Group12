from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from animals_proj.accounts.models import Profile


ALLOWED_SUBMITTER_ROLES = {
    Profile.Role.CITIZEN_SCIENTIST,
    Profile.Role.RESEARCHER,
    Profile.Role.MODERATOR,
}


class ProfileAccessMixin:
    def get_profile(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class VerifiedSubmitterRequiredMixin(LoginRequiredMixin, ProfileAccessMixin):
    permission_denied_message = 'Only verified researchers or citizen scientists can submit recordings.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        profile = self.get_profile()
        if profile.verified and profile.role in ALLOWED_SUBMITTER_ROLES:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, self.permission_denied_message)
        raise PermissionDenied(self.permission_denied_message)


class ModeratorRequiredMixin(LoginRequiredMixin, ProfileAccessMixin):
    permission_denied_message = 'Only moderators or admins can review flagged submissions.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        profile = self.get_profile()
        if request.user.is_staff or request.user.is_superuser or profile.is_moderator:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, self.permission_denied_message)
        raise PermissionDenied(self.permission_denied_message)


class OwnerOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    permission_denied_message = 'You can only edit or delete your own submissions.'

    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_authenticated and obj.can_edit(self.request.user)
