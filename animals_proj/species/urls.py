from django.urls import path
from . import views

app_name = 'species'

urlpatterns = [
    path('', views.SpeciesListView.as_view(), name='list'),
    path('<int:pk>/', views.SpeciesDetailView.as_view(), name='detail'),
]
