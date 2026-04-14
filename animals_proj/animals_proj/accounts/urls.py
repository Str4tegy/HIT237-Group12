from django.urls import path

from animals_proj.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.my_profile_redirect, name='my-profile'),
    path('profile/<slug:username>/', views.ProfileDetailView.as_view(), name='profile'),
]
