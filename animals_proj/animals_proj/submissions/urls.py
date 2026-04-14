from django.urls import path

from animals_proj.submissions import views

app_name = 'submissions'

urlpatterns = [
    path('', views.SubmissionListView.as_view(), name='list'),
    path('new/', views.SubmissionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SubmissionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SubmissionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.SubmissionDeleteView.as_view(), name='delete'),
]
