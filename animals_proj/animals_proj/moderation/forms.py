from django import forms

from animals_proj.moderation.models import Flag


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ['reason']
        widgets = {'reason': forms.Textarea(attrs={'rows': 4})}


class FlagReviewForm(forms.Form):
    decision = forms.ChoiceField(choices=[
        (Flag.Decision.DISMISSED, 'Dismiss flag and restore public status'),
        (Flag.Decision.MARK_UNDER_REVIEW, 'Keep submission under review'),
        (Flag.Decision.REMOVE_SUBMISSION, 'Remove submission from public view'),
    ])
    reviewer_notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
