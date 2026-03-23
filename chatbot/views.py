from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
import json
import re

from .models import ChatSession, ChatMessage, FAQ, FAQCategory, CareerTip, UserFeedback
from .forms import ChatMessageForm, UserFeedbackForm


def find_matching_faq(user_message):
    """Find matching FAQ based on user message"""
    user_message_lower = user_message.lower()
    
    faqs = FAQ.objects.filter(is_active=True)
    best_match = None
    highest_match_count = 0
    
    for faq in faqs:
        keywords = faq.get_keywords_list()
        match_count = sum(1 for keyword in keywords if keyword in user_message_lower)
        
        if match_count > highest_match_count:
            highest_match_count = match_count
            best_match = faq
    
    return best_match if highest_match_count > 0 else None


def generate_bot_response(user_message, user):
    """Generate bot response based on user message"""
    
    # Check for FAQ match
    faq = find_matching_faq(user_message)
    if faq:
        faq.views_count += 1
        faq.save(update_fields=['views_count'])
        return faq.answer, 'faq', 0.9
    
    # Career-related keywords
    career_keywords = {
        'resume': 'To improve your resume, focus on action verbs, quantifiable achievements, and relevant keywords.',
        'cv': 'Your CV should be concise, well-formatted, and highlight your key achievements and skills.',
        'interview': 'Prepare for interviews by researching the company, practicing common questions, and preparing examples.',
        'salary': 'When negotiating salary, research market rates, know your worth, and practice your pitch.',
        'skills': 'Develop your skills through online courses, projects, and hands-on experience.',
        'job': 'Start your job search by updating your profile, networking, and applying to relevant positions.',
    }
    
    for keyword, response in career_keywords.items():
        if keyword in user_message.lower():
            return response, 'career_advice', 0.7
    
    # Default response
    default_response = (
        "I'm here to help with career guidance! You can ask me about:\n"
        "- Resume and CV optimization\n"
        "- Interview preparation\n"
        "- Salary negotiation\n"
        "- Skill development\n"
        "- Job search strategies\n\n"
        "Or type 'FAQ' to see frequently asked questions."
    )
    
    return default_response, 'general', 0.5


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def chat(request, session_id=None):
    """Chat interface"""
    
    if session_id:
        session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    else:
        session = ChatSession.objects.create(user=request.user)
        return redirect('chat_detail', session_id=session.pk)
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data.get('content')
            
            # Save user message
            ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=user_message
            )
            
            # Generate bot response
            bot_response, intent, confidence = generate_bot_response(user_message, request.user)
            
            # Save bot message
            ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response,
                intent=intent,
                confidence_score=confidence
            )
            
            # Update session
            session.updated_at = timezone.now()
            session.save(update_fields=['updated_at'])
            
            return redirect('chat_detail', session_id=session.pk)
    else:
        form = ChatMessageForm()
    
    messages_list = session.messages.all()
    
    context = {
        'session': session,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'chatbot/chat.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def chat_list(request):
    """List user's chat sessions"""
    sessions = ChatSession.objects.filter(user=request.user)
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'chatbot/chat_list.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_chat_session(request, session_id):
    """Delete chat session"""
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    session.delete()
    messages.success(request, 'Chat session deleted.')
    return redirect('chat_list')


@login_required(login_url='login')
@require_http_methods(["POST"])
def rename_chat_session(request, session_id):
    """Rename chat session"""
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    title = request.POST.get('title')
    
    if title:
        session.title = title
        session.save(update_fields=['title'])
        messages.success(request, 'Session renamed.')
    
    return redirect('chat_detail', session_id=session.pk)


@require_http_methods(["GET"])
def faq(request):
    """FAQ page"""
    categories = FAQCategory.objects.prefetch_related('faqs')
    
    # Search
    search = request.GET.get('search')
    if search:
        faqs = FAQ.objects.filter(
            Q(question__icontains=search) |
            Q(answer__icontains=search) |
            Q(keywords__icontains=search),
            is_active=True
        )
        context = {
            'faqs': faqs,
            'search_query': search,
        }
        return render(request, 'chatbot/faq_search.html', context)
    
    context = {
        'categories': categories,
    }
    return render(request, 'chatbot/faq.html', context)


@require_http_methods(["GET"])
def faq_detail(request, pk):
    """View FAQ detail"""
    faq_obj = get_object_or_404(FAQ, pk=pk, is_active=True)
    
    # Increment views
    faq_obj.views_count += 1
    faq_obj.save(update_fields=['views_count'])
    
    # Get related FAQs
    related_faqs = FAQ.objects.filter(
        category=faq_obj.category,
        is_active=True
    ).exclude(pk=pk)[:5]
    
    context = {
        'faq': faq_obj,
        'related_faqs': related_faqs,
    }
    return render(request, 'chatbot/faq_detail.html', context)


@require_http_methods(["GET"])
def career_tips(request):
    """View career tips"""
    tips = CareerTip.objects.all()
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        tips = tips.filter(category=category)
    
    # Featured tips
    featured_tips = tips.filter(featured=True)[:3]
    
    context = {
        'tips': tips,
        'featured_tips': featured_tips,
        'category_filter': category,
    }
    return render(request, 'chatbot/career_tips.html', context)


@require_http_methods(["GET"])
def career_tip_detail(request, pk):
    """View career tip detail"""
    tip = get_object_or_404(CareerTip, pk=pk)
    
    # Increment views
    tip.views_count += 1
    tip.save(update_fields=['views_count'])
    
    # Get related tips
    related_tips = CareerTip.objects.filter(
        category=tip.category
    ).exclude(pk=pk)[:4]
    
    context = {
        'tip': tip,
        'related_tips': related_tips,
    }
    return render(request, 'chatbot/career_tip_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def submit_feedback(request, message_id):
    """Submit feedback on bot response"""
    message = get_object_or_404(ChatMessage, pk=message_id, message_type='bot')
    
    form = UserFeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.user = request.user
        feedback.message = message
        feedback.save()
        
        return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
    
    return JsonResponse({'success': False, 'errors': form.errors})