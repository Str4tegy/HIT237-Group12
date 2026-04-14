from django.urls import path

from animals_proj.moderation import views

app_name = 'moderation'

urlpatterns = [
    path('', views.FlagListView.as_view(), name='list'),
    path('submission/<int:submission_pk>/flag/', views.FlagCreateView.as_view(), name='flag-create'),
    path('<int:pk>/', views.FlagDetailView.as_view(), name='detail'),
    path('<int:pk>/review/', views.FlagReviewView.as_view(), name='review'),
]
