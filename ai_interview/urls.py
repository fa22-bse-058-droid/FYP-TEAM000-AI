from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview_home, name='interview_home'),
    path('start/', views.start_interview, name='start_interview'),
    path('start/<int:template_id>/', views.start_interview, name='start_interview_template'),
    path('session/<int:session_id>/', views.interview_detail, name='interview_detail'),
    path('question/<int:question_id>/answer/', views.submit_answer, name='submit_answer'),
    path('session/<int:session_id>/complete/', views.complete_interview, name='complete_interview'),
    path('session/<int:session_id>/results/', views.interview_results, name='interview_results'),
    path('history/', views.interview_history, name='interview_history'),
]