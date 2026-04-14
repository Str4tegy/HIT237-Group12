from django.urls import path

from animals_proj.species import views

app_name = 'species'

urlpatterns = [
    path('', views.SpeciesListView.as_view(), name='list'),
    path('autocomplete/', views.autocomplete_species, name='autocomplete'),
    path('<int:pk>/', views.SpeciesDetailView.as_view(), name='detail'),
]
