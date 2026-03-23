from django.urls import path
from . import views

urlpatterns = [
    # Forum
    path('', views.forum_home, name='forum_home'),
    path('category/<int:pk>/', views.category_threads, name='category_threads'),
    path('thread/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('category/<int:category_pk>/create/', views.create_thread, name='create_thread'),
    path('thread/<int:thread_pk>/reply/', views.reply_thread, name='reply_thread'),
    
    # Interactions
    path('reply/<int:reply_pk>/upvote/', views.upvote_reply, name='upvote_reply'),
    path('reply/<int:reply_pk>/solution/', views.mark_solution, name='mark_solution'),
    
    # Search & Profile
    path('search/', views.search_threads, name='forum_search'),
    path('user/<str:username>/', views.user_profile, name='forum_user_profile'),
]