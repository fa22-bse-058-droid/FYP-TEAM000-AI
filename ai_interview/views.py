from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta

from .models import (
    InterviewSession, InterviewQuestion, InterviewAnswer, 
    InterviewTemplate, InterviewFeedback
)


@login_required(login_url='login')
@require_http_methods(["GET"])
def interview_home(request):
    """Mock interview home page"""
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    templates = InterviewTemplate.objects.filter(is_active=True)
    
    context = {
        'sessions': sessions,
        'templates': templates,
    }
    return render(request, 'ai_interview/interview_home.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def start_interview(request, template_id=None):
    """Start a new interview session"""
    if request.method == 'POST':
        title = request.POST.get('title')
        interview_type = request.POST.get('interview_type')
        job_role = request.POST.get('job_role')
        
        session = InterviewSession.objects.create(
            user=request.user,
            title=title,
            interview_type=interview_type,
            job_role=job_role,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Add sample questions
        questions = [
            {
                'text': 'Tell us about yourself and your professional background.',
                'difficulty': 'easy',
                'category': 'Introduction'
            },
            {
                'text': 'What are your greatest strengths and weaknesses?',
                'difficulty': 'medium',
                'category': 'Self-Assessment'
            },
            {
                'text': 'Describe a challenging project and how you overcame obstacles.',
                'difficulty': 'medium',
                'category': 'Problem Solving'
            },
            {
                'text': 'How do you handle conflicts with team members?',
                'difficulty': 'medium',
                'category': 'Communication'
            },
            {
                'text': 'What are your career goals and how does this role fit?',
                'difficulty': 'easy',
                'category': 'Career Goals'
            },
        ]
        
        for idx, q in enumerate(questions, 1):
            InterviewQuestion.objects.create(
                session=session,
                question_text=q['text'],
                difficulty=q['difficulty'],
                category=q['category'],
                order=idx
            )
        
        messages.success(request, 'Interview session started!')
        return redirect('interview_detail', session_id=session.pk)
    
    templates = InterviewTemplate.objects.filter(is_active=True)
    context = {
        'templates': templates,
    }
    return render(request, 'ai_interview/start_interview.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def interview_detail(request, session_id):
    """View interview session"""
    session = get_object_or_404(InterviewSession, pk=session_id, user=request.user)
    questions = session.questions.all()
    
    context = {
        'session': session,
        'questions': questions,
    }
    return render(request, 'ai_interview/interview_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def submit_answer(request, question_id):
    """Submit answer to a question"""
    question = get_object_or_404(InterviewQuestion, pk=question_id)
    
    if question.session.user != request.user:
        messages.error(request, 'Unauthorized')
        return redirect('interview_home')
    
    answer_text = request.POST.get('answer')
    
    # Create or update answer
    answer, created = InterviewAnswer.objects.update_or_create(
        question=question,
        defaults={
            'answer_text': answer_text,
            'is_answered': bool(answer_text),
        }
    )
    
    # Simple scoring (mock)
    if answer_text:
        answer.score = min(100, len(answer_text) / 10)  # Simple heuristic
        answer.save(update_fields=['score'])
    
    return redirect('interview_detail', session_id=question.session.pk)


@login_required(login_url='login')
@require_http_methods(["GET"])
def complete_interview(request, session_id):
    """Complete interview and generate feedback"""
    session = get_object_or_404(InterviewSession, pk=session_id, user=request.user)
    
    # Calculate overall score
    answers = session.questions.all().values_list('answers', flat=True)
    scores = []
    for answer_id in answers:
        try:
            answer = InterviewAnswer.objects.get(pk=answer_id)
            scores.append(answer.score)
        except:
            pass
    
    overall_score = sum(scores) / len(scores) if scores else 0
    
    # Update session
    session.status = 'completed'
    session.completed_at = timezone.now()
    session.overall_score = overall_score
    session.duration_minutes = int((session.completed_at - session.started_at).total_seconds() / 60)
    session.save()
    
    # Create feedback
    feedback = InterviewFeedback.objects.create(
        session=session,
        communication_score=70,
        technical_score=75,
        problem_solving_score=72,
        strengths='Clear communication and good problem-solving approach',
        improvements='Could provide more detailed examples',
        overall_feedback=f'Good interview overall. Score: {overall_score:.1f}/100'
    )
    
    messages.success(request, 'Interview completed!')
    return redirect('interview_results', session_id=session.pk)


@login_required(login_url='login')
@require_http_methods(["GET"])
def interview_results(request, session_id):
    """View interview results and feedback"""
    session = get_object_or_404(InterviewSession, pk=session_id, user=request.user)
    feedback = InterviewFeedback.objects.filter(session=session).first()
    questions = session.questions.all().prefetch_related('answers')
    
    context = {
        'session': session,
        'feedback': feedback,
        'questions': questions,
    }
    return render(request, 'ai_interview/interview_results.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def interview_history(request):
    """View interview history"""
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'ai_interview/interview_history.html', context)