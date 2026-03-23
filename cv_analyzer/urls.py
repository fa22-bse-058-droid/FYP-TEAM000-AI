from django.urls import path
from . import views

urlpatterns = [
    # CV Analysis
    path('upload/', views.upload_cv_analysis, name='upload_cv_analysis'),
    path('analyses/', views.cv_analysis_list, name='cv_analysis_list'),
    path('analyses/<int:pk>/', views.cv_analysis_detail, name='cv_analysis_detail'),
    path('analyses/<int:pk>/delete/', views.delete_cv_analysis, name='delete_cv_analysis'),
    
    # CV Comparison
    path('compare/', views.cv_comparison, name='cv_comparison'),
    
    # CV Templates
    path('templates/', views.cv_templates, name='cv_templates'),
]