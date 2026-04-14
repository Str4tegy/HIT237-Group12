from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from animals_proj.accounts.models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    affiliation = forms.CharField(required=False, max_length=255)
    role = forms.ChoiceField(choices=[
        (Profile.Role.CITIZEN_SCIENTIST, 'Citizen Scientist'),
        (Profile.Role.RESEARCHER, 'Researcher'),
    ])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'affiliation', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'affiliation': self.cleaned_data.get('affiliation', ''),
                    'role': self.cleaned_data['role'],
                    'verified': False,
                },
            )
        return user
