from django import forms

from animals_proj.species.models import Species
from animals_proj.submissions.models import Submission


class SubmissionForm(forms.ModelForm):
    species_query = forms.CharField(
        label='Species search',
        help_text='Start typing to search the fauna database, then choose a result.',
        required=False,
    )

    class Meta:
        model = Submission
        fields = [
            'species_query',
            'species',
            'audio',
            'latitude',
            'longitude',
            'captured_at',
            'confidence',
            'notes',
        ]
        widgets = {
            'species': forms.Select(attrs={'class': 'species-select'}),
            'captured_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['species'].queryset = Species.objects.order_by('common_name', 'scientific_name')
        self.fields['species'].required = True
        if self.instance.pk and self.instance.species:
            self.fields['species_query'].initial = str(self.instance.species)
