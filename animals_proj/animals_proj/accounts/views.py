from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView

from animals_proj.accounts.forms import RegisterForm
from animals_proj.accounts.models import Profile


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created. An admin can now verify your profile for audio submissions.')
        return response

    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'username': self.object.username})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        Profile.objects.get_or_create(user=user)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.profile
        context['submission_count'] = self.object.submissions.count()
        context['submissions'] = (
            self.object.submissions.select_related('species')
            .annotate(flag_count=Count('flags'))[:10]
        )
        return context


def my_profile_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    Profile.objects.get_or_create(user=request.user)
    return redirect('accounts:profile', username=request.user.username)
