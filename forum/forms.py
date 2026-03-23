from django import forms
from .models import ForumThread, ForumReply

class ForumThreadForm(forms.ModelForm):
    """Form for creating forum threads"""
    
    class Meta:
        model = ForumThread
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What\'s your question or topic?'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Provide details...'
            })
        }


class ForumReplyForm(forms.ModelForm):
    """Form for creating forum replies"""
    
    class Meta:
        model = ForumReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your reply...'
            })
        }