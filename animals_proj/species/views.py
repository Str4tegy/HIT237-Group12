from django.views.generic import ListView, DetailView
from .models import Species


class SpeciesListView(ListView):
    model = Species
    template_name = 'species/list.html'
    context_object_name = 'species_list'
    paginate_by = 25


class SpeciesDetailView(DetailView):
    model = Species
    template_name = 'species/detail.html'
    context_object_name = 'species'
