"""
submissions/urls.py

URL configuration for the submissions app.
"""

from django.urls import path

from . import views

app_name = "submissions"

urlpatterns = [
    # ------------------------------------------------------------------ #
    # Home                                                                #
    # ------------------------------------------------------------------ #
    path(
        "",
        views.HomeView.as_view(),
        name="home",
    ),

    # ------------------------------------------------------------------ #
    # Submission CRUD                                                     #
    # ------------------------------------------------------------------ #
    path(
        "submissions/",
        views.SubmissionListView.as_view(),
        name="list",
    ),
    path(
        "submissions/new/",
        views.SubmissionCreateView.as_view(),
        name="create",
    ),
    path(
        "submissions/<int:pk>/",
        views.SubmissionDetailView.as_view(),
        name="detail",
    ),
    path(
        "submissions/<int:pk>/edit/",
        views.SubmissionUpdateView.as_view(),
        name="update",
    ),
    path(
        "submissions/<int:pk>/delete/",
        views.SubmissionDeleteView.as_view(),
        name="delete",
    ),

    # ------------------------------------------------------------------ #
    # Flagging                                                            #
    # ------------------------------------------------------------------ #
    path(
        "submissions/<int:submission_pk>/flag/",
        views.FlagCreateView.as_view(),
        name="flag_create",
    ),

    # ------------------------------------------------------------------ #
    # Moderation queue                                                    #
    # ------------------------------------------------------------------ #
    path(
        "moderation/flags/",
        views.FlagQueueView.as_view(),
        name="flag_queue",
    ),
    path(
        "moderation/flags/<int:pk>/resolve/",
        views.FlagResolveView.as_view(),
        name="flag_resolve",
    ),
]
