from django.urls import path
from . import views

urlpatterns = [
    # Job listings
    path('', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('recommended/', views.recommended_jobs, name='recommended_jobs'),
    
    # Applications
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    
    # Saved jobs
    path('saved/', views.saved_jobs, name='saved_jobs'),
    path('jobs/<int:pk>/save/', views.save_job, name='save_job'),
    path('jobs/<int:pk>/unsave/', views.unsave_job, name='unsave_job'),
    
    # Job alerts
    path('alerts/create/', views.create_job_alert, name='create_job_alert'),
    path('alerts/', views.my_job_alerts, name='my_job_alerts'),
    path('alerts/<int:pk>/delete/', views.delete_job_alert, name='delete_job_alert'),
    
    # Companies
    path('companies/', views.companies, name='companies'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
]