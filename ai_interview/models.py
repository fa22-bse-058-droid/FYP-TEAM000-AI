from django.db import models
from django.contrib.auth.models import User

class InterviewSession(models.Model):
    """Mock interview sessions"""
    INTERVIEW_TYPE = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('mixed', 'Mixed'),
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    
    title = models.CharField(max_length=200)
    interview_type = models.CharField(max_length=50, choices=INTERVIEW_TYPE)
    job_role = models.CharField(max_length=200, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    overall_score = models.FloatField(default=0)  # 0-100
    
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interview_session'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class InterviewQuestion(models.Model):
    """Questions for mock interviews"""
    DIFFICULTY_LEVEL = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    
    question_text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVEL)
    category = models.CharField(max_length=100)  # e.g., "Problem Solving", "Communication"
    
    order = models.IntegerField()
    
    class Meta:
        db_table = 'ai_interview_question'
        ordering = ['order']
    
    def __str__(self):
        return self.question_text[:100]


class InterviewAnswer(models.Model):
    """Answers provided by users"""
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='answers')
    
    answer_text = models.TextField()
    
    # Scoring
    score = models.FloatField(default=0)  # 0-100
    feedback = models.TextField(blank=True, null=True)
    
    # Details
    duration_seconds = models.IntegerField(default=0)
    is_answered = models.BooleanField(default=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interview_answer'
    
    def __str__(self):
        return f"Answer to {self.question.question_text[:50]}"


class InterviewTemplate(models.Model):
    """Predefined interview templates"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    interview_type = models.CharField(max_length=50)
    job_roles = models.CharField(max_length=500)  # Comma-separated
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interview_template'
    
    def __str__(self):
        return self.name


class InterviewFeedback(models.Model):
    """Feedback for completed interviews"""
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='feedback')
    
    # Scores by category
    communication_score = models.FloatField(default=0)
    technical_score = models.FloatField(default=0)
    problem_solving_score = models.FloatField(default=0)
    
    # Feedback
    strengths = models.TextField(blank=True, null=True)
    improvements = models.TextField(blank=True, null=True)
    overall_feedback = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interview_feedback'
    
    def __str__(self):
        return f"Feedback for {self.session.title}"