from django import forms
from .models import UserResourceProgress

class ResourceFilterForm(forms.Form):
    """Filter resources"""
    RESOURCE_CHOICES = [
        ('', 'All Types'),
        ('course', 'Course'),
        ('article', 'Article'),
        ('tutorial', 'Tutorial'),
        ('video', 'Video'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search resources...',
        })
    )
    
    resource_type = forms.ChoiceField(
        required=False,
        choices=RESOURCE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    difficulty = forms.ChoiceField(
        required=False,
        choices=DIFFICULTY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )