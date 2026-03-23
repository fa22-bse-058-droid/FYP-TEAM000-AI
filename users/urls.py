from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('upload-cv/', views.upload_cv, name='upload_cv'),
    
    # Password Reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('reset-password/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]