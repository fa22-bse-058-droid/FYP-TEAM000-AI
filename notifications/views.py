from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone

from .models import Notification, NotificationPreference


@login_required(login_url='login')
@require_http_methods(["GET"])
def notifications(request):
    """View all notifications"""
    notifications = Notification.objects.filter(user=request.user, is_archived=False)
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notifications.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return JsonResponse({'success': True})


@login_required(login_url='login')
@require_http_methods(["POST"])
def archive_notification(request, notification_id):
    """Archive notification"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_archived = True
    notification.save()
    
    return JsonResponse({'success': True})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def notification_preferences(request):
    """Manage notification preferences"""
    try:
        preferences = NotificationPreference.objects.get(user=request.user)
    except NotificationPreference.DoesNotExist:
        preferences = NotificationPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
        preferences.email_on_job_match = request.POST.get('email_on_job_match') == 'on'
        preferences.email_on_application_update = request.POST.get('email_on_application_update') == 'on'
        preferences.email_on_forum_reply = request.POST.get('email_on_forum_reply') == 'on'
        preferences.in_app_notifications = request.POST.get('in_app_notifications') == 'on'
        preferences.notification_frequency = request.POST.get('notification_frequency', 'instant')
        preferences.save()
        
        messages.success(request, 'Notification preferences updated!')
        return redirect('notification_preferences')
    
    context = {
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)