from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile

class CVAnalysis(models.Model):
    """Model for storing CV analysis results"""
    SCORE_CHOICES = [
        ('excellent', 'Excellent (90-100)'),
        ('good', 'Good (75-89)'),
        ('average', 'Average (60-74)'),
        ('poor', 'Poor (Below 60)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cv_analyses')
    cv_file = models.FileField(upload_to='cv_analysis/')
    
    # Analysis scores
    overall_score = models.IntegerField(default=0)
    format_score = models.IntegerField(default=0)
    content_score = models.IntegerField(default=0)
    keyword_score = models.IntegerField(default=0)
    readability_score = models.IntegerField(default=0)
    
    # Analysis details
    format_feedback = models.TextField(blank=True, null=True)
    content_feedback = models.TextField(blank=True, null=True)
    keyword_feedback = models.TextField(blank=True, null=True)
    readability_feedback = models.TextField(blank=True, null=True)
    
    # Extracted data
    extracted_skills = models.TextField(blank=True, null=True)  # JSON format
    extracted_experience = models.TextField(blank=True, null=True)  # JSON format
    extracted_education = models.TextField(blank=True, null=True)  # JSON format
    
    # Overall feedback
    overall_feedback = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)  # JSON format
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_analyzed = models.BooleanField(default=False)
    analysis_time_taken = models.FloatField(default=0)  # in seconds
    
    class Meta:
        db_table = 'cv_analyzer_cv_analysis'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CV Analysis - {self.user.username} ({self.created_at.date()})"
    
    def get_score_rating(self):
        """Return score rating based on overall_score"""
        if self.overall_score >= 90:
            return 'excellent'
        elif self.overall_score >= 75:
            return 'good'
        elif self.overall_score >= 60:
            return 'average'
        else:
            return 'poor'


class CVFeedback(models.Model):
    """Model for storing detailed CV feedback"""
    FEEDBACK_TYPE = [
        ('spelling', 'Spelling Error'),
        ('grammar', 'Grammar Error'),
        ('format', 'Format Issue'),
        ('content', 'Content Issue'),
        ('suggestion', 'Suggestion'),
    ]
    
    analysis = models.ForeignKey(CVAnalysis, on_delete=models.CASCADE, related_name='feedback_items')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE)
    section = models.CharField(max_length=100)  # e.g., "Summary", "Experience", "Skills"
    issue = models.TextField()
    suggestion = models.TextField()
    severity = models.CharField(max_length=20, choices=[('critical', 'Critical'), ('major', 'Major'), ('minor', 'Minor')])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cv_analyzer_cv_feedback'
        ordering = ['severity']
    
    def __str__(self):
        return f"{self.feedback_type} - {self.section}"


class CVTemplate(models.Model):
    """Model for CV templates"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    template_file = models.FileField(upload_to='cv_templates/')
    preview_image = models.ImageField(upload_to='cv_template_previews/')
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cv_analyzer_cv_template'
    
    def __str__(self):
        return self.name


class KeywordDatabase(models.Model):
    """Model for storing industry keywords"""
    industry = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    keywords = models.TextField()  # Comma-separated keywords
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cv_analyzer_keyword_database'
        unique_together = ('industry', 'job_title')
    
    def __str__(self):
        return f"{self.industry} - {self.job_title}"
    
    def get_keywords_list(self):
        return [kw.strip() for kw in self.keywords.split(',')]