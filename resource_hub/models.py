from django.db import models
from django.contrib.auth.models import User

class ResourceCategory(models.Model):
    """Categories for learning resources"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'resource_hub_category'
        verbose_name_plural = 'Resource Categories'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Resource(models.Model):
    """Learning resources (courses, articles, tutorials)"""
    RESOURCE_TYPE = [
        ('course', 'Course'),
        ('article', 'Article'),
        ('tutorial', 'Tutorial'),
        ('video', 'Video'),
        ('book', 'Book'),
    ]
    
    DIFFICULTY_LEVEL = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=300)
    description = models.TextField()
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVEL)
    
    # Content
    content = models.TextField(blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='resource_thumbnails/', blank=True, null=True)
    
    # Metadata
    author = models.CharField(max_length=200, blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    skills_covered = models.TextField(blank=True, null=True)  # Comma-separated
    
    # Engagement
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resource_hub_resource'
        ordering = ['-featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_skills_list(self):
        if self.skills_covered:
            return [skill.strip() for skill in self.skills_covered.split(',')]
        return []


class UserResourceProgress(models.Model):
    """Track user progress on resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_progress')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='user_progress')
    
    is_completed = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)
    progress_percentage = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'resource_hub_user_progress'
        unique_together = ('user', 'resource')
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"


class SkillPath(models.Model):
    """Curated learning paths for skill development"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    target_skill = models.CharField(max_length=100)
    resources = models.ManyToManyField(Resource, related_name='skill_paths')
    
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    estimated_hours = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resource_hub_skill_path'
    
    def __str__(self):
        return self.name