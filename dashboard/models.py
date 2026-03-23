from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserActivity(models.Model):
    """Model to track user activity"""
    ACTIVITY_TYPE = [
        ('cv_analysis', 'CV Analysis'),
        ('job_applied', 'Job Applied'),
        ('job_saved', 'Job Saved'),
        ('forum_post', 'Forum Post'),
        ('profile_updated', 'Profile Updated'),
        ('cv_uploaded', 'CV Uploaded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE)
    description = models.TextField()
    related_object_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dashboard_user_activity'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class UserStats(models.Model):
    """Model to store user statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    
    # Counters
    total_job_applications = models.IntegerField(default=0)
    saved_jobs_count = models.IntegerField(default=0)
    cv_analyses_count = models.IntegerField(default=0)
    forum_posts_count = models.IntegerField(default=0)
    
    # Dates
    last_job_applied = models.DateTimeField(blank=True, null=True)
    last_cv_analyzed = models.DateTimeField(blank=True, null=True)
    last_profile_update = models.DateTimeField(blank=True, null=True)
    
    # Goals
    monthly_applications_goal = models.IntegerField(default=10)
    weekly_applications_goal = models.IntegerField(default=3)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_user_stats'
    
    def __str__(self):
        return f"Stats for {self.user.username}"
    
    def get_applications_progress(self):
        """Calculate application progress percentage"""
        applications = self.user.job_applications.filter(
            applied_date__month=timezone.now().month
        ).count()
        progress = int((applications / self.monthly_applications_goal) * 100)
        return min(progress, 100)


class GoalTracker(models.Model):
    """Model for tracking user career goals"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress_percentage = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_goal_tracker'
        ordering = ['-target_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"