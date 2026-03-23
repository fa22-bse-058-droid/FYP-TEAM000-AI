from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone

from .models import ResourceCategory, Resource, UserResourceProgress, SkillPath
from .forms import ResourceFilterForm


@require_http_methods(["GET"])
def resource_hub(request):
    """Main resource hub page"""
    categories = ResourceCategory.objects.all()
    featured_resources = Resource.objects.filter(featured=True, is_active=True)[:6]
    
    context = {
        'categories': categories,
        'featured_resources': featured_resources,
    }
    return render(request, 'resource_hub/resource_hub.html', context)


@require_http_methods(["GET"])
def browse_resources(request):
    """Browse and filter resources"""
    resources = Resource.objects.filter(is_active=True)
    
    form = ResourceFilterForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        resource_type = form.cleaned_data.get('resource_type')
        difficulty = form.cleaned_data.get('difficulty')
        
        if search:
            resources = resources.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(skills_covered__icontains=search)
            )
        
        if resource_type:
            resources = resources.filter(resource_type=resource_type)
        
        if difficulty:
            resources = resources.filter(difficulty_level=difficulty)
    
    context = {
        'resources': resources,
        'form': form,
    }
    return render(request, 'resource_hub/browse_resources.html', context)


@require_http_methods(["GET"])
def resource_detail(request, pk):
    """View resource details"""
    resource = get_object_or_404(Resource, pk=pk, is_active=True)
    
    # Increment views
    resource.views_count += 1
    resource.save(update_fields=['views_count'])
    
    # Get user progress if authenticated
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserResourceProgress.objects.get_or_create(
            user=request.user,
            resource=resource
        )
    
    # Get related resources
    related_resources = Resource.objects.filter(
        category=resource.category,
        is_active=True
    ).exclude(pk=pk)[:5]
    
    context = {
        'resource': resource,
        'user_progress': user_progress,
        'related_resources': related_resources,
    }
    return render(request, 'resource_hub/resource_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def like_resource(request, pk):
    """Like a resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    progress, created = UserResourceProgress.objects.get_or_create(
        user=request.user,
        resource=resource
    )
    
    if progress.is_liked:
        progress.is_liked = False
        resource.likes_count -= 1
        messages.info(request, 'Removed from favorites')
    else:
        progress.is_liked = True
        resource.likes_count += 1
        messages.success(request, 'Added to favorites')
    
    progress.save()
    resource.save(update_fields=['likes_count'])
    
    return redirect('resource_detail', pk=pk)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mark_resource_complete(request, pk):
    """Mark resource as complete"""
    resource = get_object_or_404(Resource, pk=pk)
    
    progress, created = UserResourceProgress.objects.get_or_create(
        user=request.user,
        resource=resource
    )
    
    progress.is_completed = True
    progress.completed_at = timezone.now()
    progress.progress_percentage = 100
    progress.save()
    
    messages.success(request, f'Completed: {resource.title}')
    return redirect('resource_detail', pk=pk)


@require_http_methods(["GET"])
def skill_paths(request):
    """View learning paths"""
    paths = SkillPath.objects.all()
    
    # Filter by skill if provided
    target_skill = request.GET.get('skill')
    if target_skill:
        paths = paths.filter(target_skill__icontains=target_skill)
    
    context = {
        'paths': paths,
        'target_skill': target_skill,
    }
    return render(request, 'resource_hub/skill_paths.html', context)


@require_http_methods(["GET"])
def skill_path_detail(request, pk):
    """View skill path details"""
    path = get_object_or_404(SkillPath, pk=pk)
    resources = path.resources.filter(is_active=True)
    
    context = {
        'path': path,
        'resources': resources,
    }
    return render(request, 'resource_hub/skill_path_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def my_learning(request):
    """View user's learning progress"""
    progress = UserResourceProgress.objects.filter(user=request.user)
    
    # Filter by completion status
    status = request.GET.get('status')
    if status == 'completed':
        progress = progress.filter(is_completed=True)
    elif status == 'in_progress':
        progress = progress.filter(is_completed=False)
    
    context = {
        'progress': progress,
        'status': status,
    }
    return render(request, 'resource_hub/my_learning.html', context)