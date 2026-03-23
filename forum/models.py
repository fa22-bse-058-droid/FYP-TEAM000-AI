from django.db import models
from django.contrib.auth.models import User

class ForumCategory(models.Model):
    """Model for forum categories"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=20, default='primary')
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'forum_category'
        verbose_name_plural = 'Forum Categories'
        ordering = ['order']
    
    def __str__(self):
        return self.name
    
    def get_thread_count(self):
        return self.threads.count()


class ForumThread(models.Model):
    """Model for forum threads/discussions"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pinned', 'Pinned'),
        ('locked', 'Locked'),
    ]
    
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_threads')
    
    title = models.CharField(max_length=300)
    content = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    views_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_thread'
        ordering = ['-is_featured', '-updated_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title


class ForumReply(models.Model):
    """Model for forum replies"""
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_reply'
        ordering = ['-is_solution', '-upvotes', 'created_at']
    
    def __str__(self):
        return f"Reply by {self.author.username} on {self.thread.title}"


class ForumUpvote(models.Model):
    """Model for upvotes on replies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_upvotes')
    reply = models.ForeignKey(ForumReply, on_delete=models.CASCADE, related_name='upvoted_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_upvote'
        unique_together = ('user', 'reply')
    
    def __str__(self):
        return f"{self.user.username} upvoted {self.reply.id}"


class UserBadge(models.Model):
    """Model for user badges/reputation"""
    BADGE_TYPE = [
        ('contributor', 'Contributor'),
        ('expert', 'Expert'),
        ('helpful', 'Helpful'),
        ('active', 'Active Member'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_badges')
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPE)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_user_badge'
        unique_together = ('user', 'badge_type')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"


class UserReputation(models.Model):
    """Model for user reputation points"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forum_reputation')
    reputation_points = models.IntegerField(default=0)
    threads_created = models.IntegerField(default=0)
    helpful_replies = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'forum_user_reputation'
    
    def __str__(self):
        return f"{self.user.username} - {self.reputation_points} points"