from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_hub, name='resource_hub'),
    path('browse/', views.browse_resources, name='browse_resources'),
    path('resource/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resource/<int:pk>/like/', views.like_resource, name='like_resource'),
    path('resource/<int:pk>/complete/', views.mark_resource_complete, name='mark_resource_complete'),
    
    path('paths/', views.skill_paths, name='skill_paths'),
    path('paths/<int:pk>/', views.skill_path_detail, name='skill_path_detail'),
    
    path('my-learning/', views.my_learning, name='my_learning'),
]