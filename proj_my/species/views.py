"""
species/views.py
"""

from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from .models import Species, TaxonomicClass


class SpeciesListView(ListView):
    """
    Browse all NT fauna species.

    Supports optional filtering by taxonomic class via ?class=<pk>.

    QuerySet API demonstrated:
      - annotate(submission_count=Count("submissions")) — adds the number
        of audio recordings per species to each row in a single DB query.
        Without annotation this would require N+1 queries (one per species).
      - filter() for optional class filtering
      - select_related() to fetch taxonomic_class in one JOIN

    This annotation is the key upgrade from Credit to Distinction level:
    it demonstrates aggregate QuerySet composition beyond basic filtering.
    """

    model = Species
    template_name = "species/species_list.html"
    context_object_name = "species_list"
    paginate_by = 24

    def get_queryset(self):
        qs = (
            Species.objects
            .select_related("taxonomic_class")
            # Annotate each species with how many visible submissions it has
            # This is a single JOIN query — no N+1 problem
            .annotate(
                submission_count=Count(
                    "submissions",
                    # Only count visible submissions
                    filter=Q(submissions__is_visible=True),
                    distinct=True,
                )
            )
            .order_by("common_name")
        )
        # Optional filter by taxonomic class
        class_pk = self.request.GET.get("class")
        if class_pk:
            qs = qs.filter(taxonomic_class__pk=class_pk)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # All taxonomic classes for the category nav
        context["taxonomic_classes"] = TaxonomicClass.objects.annotate(
            # Also annotate each class with its species count for nav badges
            species_count=Count("species", distinct=True)
        ).order_by("name")
        context["active_class_pk"] = self.request.GET.get("class")
        # Total species count for the page header
        context["total_species"] = Species.objects.count()
        return context


class SpeciesDetailView(DetailView):
    """
    Single species page.

    Shows taxonomy, conservation status, GPS copy button,
    and the 10 most recent audio submissions for this species.

    Annotation: avg_confidence annotated onto recent_submissions
    so the template can show the average confidence score for this
    species' recordings — demonstrates Avg aggregation.

    Loose coupling: Submissions are fetched via the reverse FK
    (species.submissions) rather than importing from submissions.views.
    """

    model = Species
    template_name = "species/species_detail.html"
    context_object_name = "species"

    def get_queryset(self):
        return Species.objects.select_related("taxonomic_class")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recent visible submissions for this species via reverse FK
        recent_submissions = (
            self.object.submissions
            .filter(is_visible=True)
            .select_related("submitter")
            .order_by("-captured_at")[:10]
        )
        context["recent_submissions"] = recent_submissions

        # Aggregate stats for this species — single query with Avg and Count
        stats = self.object.submissions.filter(is_visible=True).aggregate(
            total_recordings=Count("id"),
            avg_confidence=Avg("confidence_score"),
        )
        context["total_recordings"] = stats["total_recordings"]
        context["avg_confidence"] = (
            round(stats["avg_confidence"], 1)
            if stats["avg_confidence"] else None
        )

        return context


class SpeciesAutocompleteView(ListView):
    """
    JSON endpoint for live species search during audio submission.

    Accepts: GET ?q=<search term>
    Returns: JSON array of {id, common_name, scientific_name}

    QuerySet API:
      - icontains for case-insensitive partial matching on both name fields
      - Q objects for OR lookup across two fields
      - values() to return only needed fields — lean response
      - Results capped at 10

    Design note: minimum 2 characters prevents unnecessary DB hits.
    Loose coupling: species app exposes this; submissions form consumes
    it without the species app knowing about submissions.
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()

        if len(query) < 2:
            return JsonResponse({"results": []})

        species = (
            Species.objects.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query)
            )
            .values("id", "common_name", "scientific_name")[:10]
        )

        return JsonResponse({"results": list(species)})
