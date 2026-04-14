from django.views.generic import ListView, DetailView
from .models import Submission


class SubmissionListView(ListView):
    model = Submission
    template_name = 'submissions/list.html'
    context_object_name = 'submissions'
    paginate_by = 20


class SubmissionDetailView(DetailView):
    model = Submission
    template_name = 'submissions/detail.html'
    context_object_name = 'submission'
