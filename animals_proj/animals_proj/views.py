from django.db.models import Count
from django.views.generic import TemplateView

from animals_proj.submissions.models import Submission


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_entries = (
            Submission.objects.visible_to(self.request.user)
            .select_related('species', 'submitter')
            .annotate(flag_count=Count('flags'))[:8]
        )
        context['recent_entries'] = recent_entries
        return context
