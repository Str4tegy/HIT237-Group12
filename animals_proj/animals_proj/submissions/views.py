from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from animals_proj.permissions import OwnerOrAdminRequiredMixin, VerifiedSubmitterRequiredMixin
from animals_proj.submissions.forms import SubmissionForm
from animals_proj.submissions.models import Submission


class SubmissionListView(ListView):
    model = Submission
    template_name = 'submissions/list.html'
    context_object_name = 'submissions'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Submission.objects.visible_to(self.request.user)
            .select_related('species', 'submitter')
            .annotate(flag_count=Count('flags'))
        )
        status = self.request.GET.get('status', '').strip()
        mine = self.request.GET.get('mine', '').strip()
        query = self.request.GET.get('q', '').strip()

        if status:
            queryset = queryset.filter(status=status)
        if mine and self.request.user.is_authenticated:
            queryset = queryset.for_owner(self.request.user)
        return queryset.search(query).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', '')
        context['mine'] = self.request.GET.get('mine', '')
        context['status_choices'] = Submission.Status.choices
        return context


class SubmissionDetailView(DetailView):
    model = Submission
    template_name = 'submissions/detail.html'
    context_object_name = 'submission'

    def get_queryset(self):
        return Submission.objects.visible_to(self.request.user).select_related('species', 'submitter').prefetch_related('flags')


class SubmissionCreateView(VerifiedSubmitterRequiredMixin, CreateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'submissions/form.html'

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        messages.success(self.request, 'Recording submission created successfully.')
        return super().form_valid(form)


class SubmissionUpdateView(OwnerOrAdminRequiredMixin, UpdateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'submissions/form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Submission updated successfully.')
        return super().form_valid(form)


class SubmissionDeleteView(OwnerOrAdminRequiredMixin, DeleteView):
    model = Submission
    template_name = 'submissions/confirm_delete.html'
    success_url = reverse_lazy('submissions:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Submission deleted successfully.')
        return super().delete(request, *args, **kwargs)
