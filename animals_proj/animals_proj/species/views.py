from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from animals_proj.species.models import Species


class SpeciesListView(ListView):
    model = Species
    template_name = 'species/list.html'
    context_object_name = 'species_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = Species.objects.annotate(submission_count=Count('submissions'))
        query = self.request.GET.get('q', '').strip()
        taxon_class = self.request.GET.get('taxon_class', '').strip()

        if query:
            queryset = queryset.filter(
                Q(common_name__icontains=query) | Q(scientific_name__icontains=query)
            )
        if taxon_class:
            queryset = queryset.filter(taxon_class__iexact=taxon_class)
        return queryset.order_by('common_name', 'scientific_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['taxon_class'] = self.request.GET.get('taxon_class', '')
        context['available_classes'] = (
            Species.objects.exclude(taxon_class='')
            .order_by('taxon_class')
            .values_list('taxon_class', flat=True)
            .distinct()
        )
        return context


class SpeciesDetailView(DetailView):
    model = Species
    template_name = 'species/detail.html'
    context_object_name = 'species'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_submissions'] = self.object.submissions.visible_to(self.request.user).select_related('submitter')[:8]
        return context


def autocomplete_species(request):
    query = request.GET.get('q', '').strip()
    queryset = Species.objects.all()
    if query:
        queryset = queryset.filter(
            Q(common_name__icontains=query) | Q(scientific_name__icontains=query)
        )
    data = [
        {
            'id': species.id,
            'label': str(species),
            'scientific_name': species.scientific_name,
            'common_name': species.common_name,
        }
        for species in queryset.order_by('common_name', 'scientific_name')[:10]
    ]
    return JsonResponse({'results': data})
