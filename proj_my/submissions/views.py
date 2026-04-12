"""
submissions/views.py
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from species.models import Species
from .models import AudioSubmission, SubmissionFlag


# Reusable mixins — DRY permission enforcement                        

class VerifiedUserMixin(LoginRequiredMixin):
    """
    Restricts a view to logged-in users who have a submittable role
    (Citizen Scientist, Researcher, Moderator, or Admin).

    Used on: SubmissionCreateView, FlagCreateView

    Django philosophy: Explicit is better than implicit — the role check
    is visible here, not buried in a permission table.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_researcher_or_above:
            messages.error(
                request,
                "You need a verified account to submit recordings.",
            )
            return redirect("submissions:list")
        return super().dispatch(request, *args, **kwargs)


class SubmitterOrAdminMixin(LoginRequiredMixin):
    """
    Restricts edit/delete views to the original submitter or an admin.

    Delegates to User.can_edit() / User.can_delete() defined on the
    User model — permission logic is centralised there (DRY).

    Used on: SubmissionUpdateView, SubmissionDeleteView
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.can_edit(obj):
            self._permission_denied = True
        return obj

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.object = self.get_object()
        if getattr(self, "_permission_denied", False):
            messages.error(
                request,
                "You do not have permission to edit this submission.",
            )
            return redirect("submissions:detail", pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)


class ModeratorRequiredMixin(LoginRequiredMixin):
    """
    Restricts a view to users with moderator or admin role.

    Used on: FlagQueueView, FlagResolveView
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_moderator:
            messages.error(request, "Moderator access required.")
            return redirect("submissions:list")
        return super().dispatch(request, *args, **kwargs)


# ------------------------------------------------------------------ #
# Home view                                                           #
# ------------------------------------------------------------------ #

class HomeView(ListView):
    """
    Homepage: displays the most recent 10 visible audio submissions
    as a timeline feed.

    QuerySet: Uses the custom manager's for_public_display() method
    which chains visible() + select_related() + order_by() in one
    reusable call — DRY, no duplication with SubmissionListView.
    """

    model = AudioSubmission
    template_name = "submissions/home.html"
    context_object_name = "submissions"

    def get_queryset(self):
        """
        Uses custom manager method — query logic lives in managers.py,
        not duplicated here and in SubmissionListView.
        """
        return AudioSubmission.objects.for_public_display()[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Total submission count for the homepage stats banner
        context["total_submissions"] = AudioSubmission.objects.visible().count()
        # Total species with at least one submission — distinct annotation
        context["active_species_count"] = (
            AudioSubmission.objects.visible()
            .values("species")
            .distinct()
            .count()
        )
        return context


# ------------------------------------------------------------------ #
# Submission list & detail                                            #
# ------------------------------------------------------------------ #

class SubmissionListView(ListView):
    """
    Browsable list of all visible audio submissions.
    Supports optional filtering by species via ?species=<pk> query param.

    QuerySet API demonstrated:
      - Custom manager for_public_display() composes visible() +
        select_related() + order_by() — DRY
      - with_flag_counts() annotation adds open_flag_count to each
        submission so moderators can see flagged entries in the list
      - Optional species filter via .by_species()
    """

    model = AudioSubmission
    template_name = "submissions/submission_list.html"
    context_object_name = "submissions"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            AudioSubmission.objects
            .for_public_display()
            .order_by("-captured_at")
        )
        # Optional species filter
        species_pk = self.request.GET.get("species")
        if species_pk:
            qs = qs.filter(species__pk=species_pk)

        # Annotate with open flag count for moderators
        if self.request.user.is_authenticated and self.request.user.is_moderator:
            qs = qs.with_flag_counts()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        species_pk = self.request.GET.get("species")
        if species_pk:
            context["filtered_species"] = Species.objects.filter(pk=species_pk).first()
        return context


class SubmissionDetailView(DetailView):
    """
    Single submission page.

    Shows the audio player, metadata, submitter profile snippet,
    and a flag button for logged-in users.

    Annotation: species_submission_count added to context via a
    single count() call — avoids loading all related objects.
    """

    model = AudioSubmission
    template_name = "submissions/submission_detail.html"
    context_object_name = "submission"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_moderator:
            return AudioSubmission.objects.select_related(
                "species", "submitter", "species__taxonomic_class"
            )
        return AudioSubmission.objects.visible().select_related(
            "species", "submitter", "species__taxonomic_class"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        user = self.request.user

        context["already_flagged"] = (
            user.is_authenticated
            and submission.flags.filter(reporter=user).exists()
        )
        context["can_edit"] = (
            user.is_authenticated and user.can_edit(submission)
        )
        # Other submissions by the same user — uses custom manager method
        context["other_submissions"] = (
            AudioSubmission.objects.visible()
            .by_submitter(submission.submitter)
            .exclude(pk=submission.pk)
            .select_related("species")
            .order_by("-created_at")[:5]
        )
        # How many recordings of this species exist — single count query
        context["species_submission_count"] = (
            AudioSubmission.objects.visible()
            .by_species(submission.species)
            .count()
        )
        return context


# ------------------------------------------------------------------ #
# Submission create / update / delete                                 #
# ------------------------------------------------------------------ #

class SubmissionCreateView(VerifiedUserMixin, CreateView):
    """
    Form for verified users to submit a new audio recording entry.
    Sets submitter automatically from request.user.
    """

    model = AudioSubmission
    template_name = "submissions/submission_form.html"
    fields = [
        "species",
        "audio_file",
        "captured_at",
        "latitude",
        "longitude",
        "location_notes",
        "confidence_score",
        "notes",
    ]

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        messages.success(self.request, "Your recording has been submitted.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["species_list"] = Species.objects.order_by("common_name")
        return context


class SubmissionUpdateView(SubmitterOrAdminMixin, UpdateView):
    """
    Edit an existing submission.
    Restricted to the original submitter or an admin.
    """

    model = AudioSubmission
    template_name = "submissions/submission_form.html"
    fields = [
        "species",
        "audio_file",
        "captured_at",
        "latitude",
        "longitude",
        "location_notes",
        "confidence_score",
        "notes",
    ]

    def form_valid(self, form):
        messages.success(self.request, "Submission updated successfully.")
        return super().form_valid(form)


class SubmissionDeleteView(SubmitterOrAdminMixin, DeleteView):
    """
    Delete a submission.
    Restricted to the original submitter or an admin.
    """

    model = AudioSubmission
    template_name = "submissions/submission_confirm_delete.html"
    success_url = reverse_lazy("submissions:list")

    def form_valid(self, form):
        messages.success(self.request, "Submission deleted.")
        return super().form_valid(form)


# ------------------------------------------------------------------ #
# Flagging views                                                      #
# ------------------------------------------------------------------ #

class FlagCreateView(VerifiedUserMixin, CreateView):
    """
    Any verified user can flag a submission they believe is anomalous.

    Business rules:
      - Users cannot flag their own submissions
      - A user cannot flag the same submission twice
    """

    model = SubmissionFlag
    template_name = "submissions/flag_form.html"
    fields = ["reason", "notes"]

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(
            AudioSubmission, pk=kwargs["submission_pk"], is_visible=True
        )
        if request.user.is_authenticated and self.submission.submitter == request.user:
            messages.error(request, "You cannot flag your own submission.")
            return redirect("submissions:detail", pk=self.submission.pk)
        if request.user.is_authenticated and self.submission.flags.filter(
            reporter=request.user
        ).exists():
            messages.info(request, "You have already flagged this submission.")
            return redirect("submissions:detail", pk=self.submission.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.submission = self.submission
        messages.success(
            self.request,
            "Flag submitted. A moderator will review this entry.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.submission.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submission"] = self.submission
        return context


class FlagQueueView(ModeratorRequiredMixin, ListView):
    """
    Moderator-only view: list of all open flags.

    QuerySet API demonstrated:
      - with_flag_counts() annotation from custom manager
      - select_related() for performance
      - FIFO ordering (oldest flags first)
      - Summary stats annotated into context
    """

    model = SubmissionFlag
    template_name = "submissions/flag_queue.html"
    context_object_name = "flags"
    paginate_by = 20

    def get_queryset(self):
        return (
            SubmissionFlag.objects.filter(status=SubmissionFlag.OPEN)
            .select_related(
                "submission",
                "submission__species",
                "submission__submitter",
                "reporter",
            )
            .order_by("created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_open_flags"] = SubmissionFlag.objects.filter(
            status=SubmissionFlag.OPEN
        ).count()
        context["flagged_submissions_count"] = (
            AudioSubmission.objects.flagged().count()
        )
        return context


class FlagResolveView(ModeratorRequiredMixin, UpdateView):
    """
    Moderator resolves a flag: dismisses or actions it.
    If actioned, sets submission.is_visible=False (soft delete).
    """

    model = SubmissionFlag
    template_name = "submissions/flag_resolve.html"
    fields = ["status", "moderator_notes"]
    success_url = reverse_lazy("submissions:flag_queue")

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.reviewed_by = self.request.user
        flag.reviewed_at = timezone.now()
        flag.save()

        if flag.status == SubmissionFlag.ACTIONED:
            flag.submission.is_visible = False
            flag.submission.save(update_fields=["is_visible"])
            messages.success(
                self.request,
                f"Flag actioned. Submission '{flag.submission}' has been hidden.",
            )
        else:
            messages.success(self.request, "Flag dismissed.")

        return redirect(self.success_url)
