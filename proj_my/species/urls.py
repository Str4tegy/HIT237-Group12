"""
species/urls.py
"""

from django.urls import path

from . import views

app_name = "species"

urlpatterns = [
    path(
        "species/",
        views.SpeciesListView.as_view(),
        name="list",
    ),
    path(
        "species/<int:pk>/",
        views.SpeciesDetailView.as_view(),
        name="detail",
    ),
    path(
        "species/autocomplete/",
        views.SpeciesAutocompleteView.as_view(),
        name="autocomplete",
    ),
]
