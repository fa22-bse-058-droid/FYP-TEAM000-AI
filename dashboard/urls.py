from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('activity/', views.activity_log, name='activity_log'),
    path('goals/', views.goal_tracker, name='goal_tracker'),
    path('goals/<int:goal_id>/update/', views.update_goal_progress, name='update_goal_progress'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('recommendations/', views.recommendations, name='recommendations'),
]