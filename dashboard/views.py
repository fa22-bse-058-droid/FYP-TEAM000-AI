from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from jobs.models import JobApplication, SavedJob
from cv_analyzer.models import CVAnalysis
from forum.models import ForumThread
from .models import UserActivity, UserStats, GoalTracker


@login_required(login_url='login')
@require_http_methods(["GET"])
def dashboard(request):
    """Main dashboard"""
    user = request.user
    
    # Get or create user stats
    try:
        stats = UserStats.objects.get(user=user)
    except UserStats.DoesNotExist:
        stats = UserStats.objects.create(user=user)
    
    # Get recent activities
    activities = UserActivity.objects.filter(user=user)[:10]
    
    # Get stats
    recent_applications = JobApplication.objects.filter(user=user).count()
    saved_jobs = SavedJob.objects.filter(user=user).count()
    cv_analyses = CVAnalysis.objects.filter(user=user).count()
    forum_posts = ForumThread.objects.filter(author=user).count()
    
    # Get this month's applications
    this_month_applications = JobApplication.objects.filter(
        user=user,
        applied_date__month=timezone.now().month
    ).count()
    
    # Get active goals
    active_goals = GoalTracker.objects.filter(user=user, status='active')
    
    context = {
        'stats': stats,
        'activities': activities,
        'recent_applications': recent_applications,
        'saved_jobs': saved_jobs,
        'cv_analyses': cv_analyses,
        'forum_posts': forum_posts,
        'this_month_applications': this_month_applications,
        'active_goals': active_goals,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def analytics(request):
    """Analytics and insights"""
    user = request.user
    
    # Job applications over time
    last_30_days = timezone.now() - timedelta(days=30)
    applications_last_30 = JobApplication.objects.filter(
        user=user,
        applied_date__gte=last_30_days
    ).count()
    
    # Applications by status
    applications_by_status = JobApplication.objects.filter(user=user).values('status').annotate(count=Count('id'))
    
    # Most applied job types
    applied_jobs = JobApplication.objects.filter(user=user).select_related('job')
    job_type_stats = {}
    for app in applied_jobs:
        job_type = app.job.job_type
        job_type_stats[job_type] = job_type_stats.get(job_type, 0) + 1
    
    context = {
        'applications_last_30': applications_last_30,
        'applications_by_status': applications_by_status,
        'job_type_stats': job_type_stats,
    }
    return render(request, 'dashboard/analytics.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def activity_log(request):
    """View activity log"""
    activities = UserActivity.objects.filter(user=request.user)
    
    # Filter by type if provided
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    context = {
        'activities': activities,
        'activity_type': activity_type,
    }
    return render(request, 'dashboard/activity_log.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def goal_tracker(request):
    """Manage career goals"""
    goals = GoalTracker.objects.filter(user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        target_date = request.POST.get('target_date')
        
        if title and target_date:
            GoalTracker.objects.create(
                user=request.user,
                title=title,
                description=description,
                target_date=target_date
            )
            messages.success(request, 'Goal created successfully!')
            return redirect('goal_tracker')
    
    context = {
        'goals': goals,
    }
    return render(request, 'dashboard/goal_tracker.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def update_goal_progress(request, goal_id):
    """Update goal progress"""
    goal = get_object_or_404(GoalTracker, pk=goal_id, user=request.user)
    progress = request.POST.get('progress')
    
    if progress:
        goal.progress_percentage = int(progress)
        goal.save(update_fields=['progress_percentage'])
        messages.success(request, 'Goal progress updated!')
    
    return redirect('goal_tracker')


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_goal(request, goal_id):
    """Delete goal"""
    goal = get_object_or_404(GoalTracker, pk=goal_id, user=request.user)
    goal.delete()
    messages.success(request, 'Goal deleted.')
    return redirect('goal_tracker')


@login_required(login_url='login')
@require_http_methods(["GET"])
def recommendations(request):
    """Get personalized recommendations"""
    user = request.user
    recommendations = []
    
    # Check CV
    cv_analyses = CVAnalysis.objects.filter(user=user)
    if not cv_analyses.exists():
        recommendations.append({
            'type': 'cv_analysis',
            'title': 'Analyze Your CV',
            'description': 'Get AI-powered feedback to improve your resume',
            'priority': 'high',
            'icon': 'fa-file-pdf'
        })
    
    # Check profile completion
    if not user.profile.bio or not user.profile.skills:
        recommendations.append({
            'type': 'profile',
            'title': 'Complete Your Profile',
            'description': 'Add bio and skills to increase job match',
            'priority': 'high',
            'icon': 'fa-user'
        })
    
    # Check applications
    this_month_apps = JobApplication.objects.filter(
        user=user,
        applied_date__month=timezone.now().month
    ).count()
    
    if this_month_apps < 3:
        recommendations.append({
            'type': 'jobs',
            'title': 'Apply to More Jobs',
            'description': f'You\'ve applied to {this_month_apps} jobs this month',
            'priority': 'medium',
            'icon': 'fa-briefcase'
        })
    
    context = {
        'recommendations': recommendations,
    }
    return render(request, 'dashboard/recommendations.html', context)