from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, FormView, ListView

from animals_proj.moderation.forms import FlagForm, FlagReviewForm
from animals_proj.moderation.models import Flag
from animals_proj.permissions import ModeratorRequiredMixin
from animals_proj.submissions.models import Submission


class FlagCreateView(LoginRequiredMixin, CreateView):
    model = Flag
    form_class = FlagForm
    template_name = 'moderation/flag_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        duplicate = Flag.objects.filter(
            submission=self.submission,
            reporter=self.request.user,
            reviewed=False,
        ).exists()
        if duplicate:
            messages.error(self.request, 'You already have an open flag for this submission.')
            return redirect(self.submission.get_absolute_url())

        form.instance.submission = self.submission
        form.instance.reporter = self.request.user
        self.submission.status = Submission.Status.FLAGGED
        self.submission.save(update_fields=['status'])
        messages.success(self.request, 'Submission flagged for moderator review.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.submission.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.submission
        return context


class FlagListView(ModeratorRequiredMixin, ListView):
    model = Flag
    template_name = 'moderation/list.html'
    context_object_name = 'flags'
    paginate_by = 20

    def get_queryset(self):
        queryset = Flag.objects.select_related('submission', 'submission__species', 'reporter', 'reviewed_by')
        filter_value = self.request.GET.get('state', 'open')
        if filter_value == 'reviewed':
            return queryset.filter(reviewed=True)
        if filter_value == 'all':
            return queryset
        return queryset.filter(reviewed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state'] = self.request.GET.get('state', 'open')
        return context


class FlagReviewView(ModeratorRequiredMixin, FormView):
    form_class = FlagReviewForm
    template_name = 'moderation/review.html'

    def dispatch(self, request, *args, **kwargs):
        self.flag = get_object_or_404(
            Flag.objects.select_related('submission', 'submission__species', 'reporter'),
            pk=kwargs['pk'],
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.flag.apply_decision(
            reviewer=self.request.user,
            notes=form.cleaned_data['reviewer_notes'],
            decision=form.cleaned_data['decision'],
        )
        messages.success(self.request, 'Flag reviewed and submission status updated.')
        return redirect('moderation:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flag'] = self.flag
        return context


class FlagDetailView(ModeratorRequiredMixin, DetailView):
    model = Flag
    template_name = 'moderation/detail.html'
    context_object_name = 'flag'
