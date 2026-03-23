from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from django.core.paginator import Paginator

from .models import ForumCategory, ForumThread, ForumReply, ForumUpvote, UserReputation
from .forms import ForumThreadForm, ForumReplyForm


@require_http_methods(["GET"])
def forum_home(request):
    """Forum home page"""
    categories = ForumCategory.objects.all()
    recent_threads = ForumThread.objects.filter(status='open').order_by('-created_at')[:10]
    
    context = {
        'categories': categories,
        'recent_threads': recent_threads,
    }
    return render(request, 'forum/forum_home.html', context)


@require_http_methods(["GET"])
def category_threads(request, pk):
    """View threads in a category"""
    category = get_object_or_404(ForumCategory, pk=pk)
    threads = category.threads.filter(status__in=['open', 'pinned'])
    
    # Pagination
    paginator = Paginator(threads, 10)
    page_number = request.GET.get('page')
    threads_page = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'threads': threads_page,
    }
    return render(request, 'forum/category_threads.html', context)


@require_http_methods(["GET"])
def thread_detail(request, pk):
    """View thread detail with replies"""
    thread = get_object_or_404(ForumThread, pk=pk)
    
    # Increment views
    thread.views_count += 1
    thread.save(update_fields=['views_count'])
    
    replies = thread.replies.all()
    
    context = {
        'thread': thread,
        'replies': replies,
    }
    return render(request, 'forum/thread_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_thread(request, category_pk):
    """Create new forum thread"""
    category = get_object_or_404(ForumCategory, pk=category_pk)
    
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.category = category
            thread.save()
            
            # Add reputation points
            try:
                reputation = UserReputation.objects.get(user=request.user)
                reputation.reputation_points += 5
                reputation.threads_created += 1
                reputation.save()
            except UserReputation.DoesNotExist:
                UserReputation.objects.create(
                    user=request.user,
                    reputation_points=5,
                    threads_created=1
                )
            
            messages.success(request, 'Thread created successfully!')
            return redirect('thread_detail', pk=thread.pk)
    else:
        form = ForumThreadForm()
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'forum/create_thread.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def reply_thread(request, thread_pk):
    """Reply to a forum thread"""
    thread = get_object_or_404(ForumThread, pk=thread_pk)
    
    if thread.status == 'locked':
        messages.error(request, 'This thread is locked and cannot accept replies.')
        return redirect('thread_detail', pk=thread.pk)
    
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.thread = thread
            reply.save()
            
            # Update thread replies count
            thread.replies_count += 1
            thread.save(update_fields=['replies_count', 'updated_at'])
            
            # Add reputation points
            try:
                reputation = UserReputation.objects.get(user=request.user)
                reputation.reputation_points += 2
                reputation.save()
            except UserReputation.DoesNotExist:
                UserReputation.objects.create(user=request.user, reputation_points=2)
            
            messages.success(request, 'Reply posted successfully!')
            return redirect('thread_detail', pk=thread.pk)
    else:
        form = ForumReplyForm()
    
    context = {
        'form': form,
        'thread': thread,
    }
    return render(request, 'forum/reply_thread.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def upvote_reply(request, reply_pk):
    """Upvote a forum reply"""
    reply = get_object_or_404(ForumReply, pk=reply_pk)
    
    upvote, created = ForumUpvote.objects.get_or_create(user=request.user, reply=reply)
    
    if created:
        reply.upvotes += 1
        reply.save(update_fields=['upvotes'])
        
        # Add reputation to author
        try:
            reputation = UserReputation.objects.get(user=reply.author)
            reputation.reputation_points += 1
            reputation.helpful_replies += 1
            reputation.save()
        except UserReputation.DoesNotExist:
            UserReputation.objects.create(
                user=reply.author,
                reputation_points=1,
                helpful_replies=1
            )
        
        return redirect('thread_detail', pk=reply.thread.pk)
    else:
        upvote.delete()
        reply.upvotes -= 1
        reply.save(update_fields=['upvotes'])
    
    return redirect('thread_detail', pk=reply.thread.pk)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mark_solution(request, reply_pk):
    """Mark reply as solution"""
    reply = get_object_or_404(ForumReply, pk=reply_pk)
    thread = reply.thread
    
    # Check if user is thread author
    if request.user != thread.author:
        messages.error(request, 'Only thread author can mark solution.')
        return redirect('thread_detail', pk=thread.pk)
    
    # Remove solution from other replies
    thread.replies.filter(is_solution=True).update(is_solution=False)
    
    # Mark this reply as solution
    reply.is_solution = True
    reply.save(update_fields=['is_solution'])
    
    messages.success(request, 'Reply marked as solution!')
    return redirect('thread_detail', pk=thread.pk)


@require_http_methods(["GET"])
def search_threads(request):
    """Search forum threads"""
    query = request.GET.get('q')
    threads = ForumThread.objects.none()
    
    if query:
        threads = ForumThread.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            status__in=['open', 'pinned']
        )
    
    context = {
        'threads': threads,
        'query': query,
    }
    return render(request, 'forum/search_results.html', context)


@require_http_methods(["GET"])
def user_profile(request, username):
    """View user profile with forum activity"""
    from django.contrib.auth.models import User as DjangoUser
    
    user = get_object_or_404(DjangoUser, username=username)
    
    threads = ForumThread.objects.filter(author=user).order_by('-created_at')
    replies = ForumReply.objects.filter(author=user).order_by('-created_at')
    
    try:
        reputation = UserReputation.objects.get(user=user)
    except UserReputation.DoesNotExist:
        reputation = None
    
    badges = user.forum_badges.all() if hasattr(user, 'forum_badges') else []
    
    context = {
        'profile_user': user,
        'threads': threads[:5],
        'replies': replies[:5],
        'reputation': reputation,
        'badges': badges,
    }
    return render(request, 'forum/user_profile.html', context)