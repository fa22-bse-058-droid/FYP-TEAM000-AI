from django.urls import path
from . import views

urlpatterns = [
    # Chat
    path('', views.chat, name='chat'),
    path('chat/<int:session_id>/', views.chat, name='chat_detail'),
    path('sessions/', views.chat_list, name='chat_list'),
    path('sessions/<int:session_id>/delete/', views.delete_chat_session, name='delete_chat_session'),
    path('sessions/<int:session_id>/rename/', views.rename_chat_session, name='rename_chat_session'),
    
    # FAQ
    path('faq/', views.faq, name='faq'),
    path('faq/<int:pk>/', views.faq_detail, name='faq_detail'),
    
    # Career Tips
    path('tips/', views.career_tips, name='career_tips'),
    path('tips/<int:pk>/', views.career_tip_detail, name='career_tip_detail'),
    
    # Feedback
    path('feedback/<int:message_id>/', views.submit_feedback, name='submit_feedback'),
]