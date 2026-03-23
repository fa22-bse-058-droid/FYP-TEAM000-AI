from django import forms
from .models import ChatMessage, UserFeedback

class ChatMessageForm(forms.ModelForm):
    """Form for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type your question...',
                'autocomplete': 'off'
            })
        }


class UserFeedbackForm(forms.ModelForm):
    """Form for feedback on bot responses"""
    
    class Meta:
        model = UserFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional comments (optional)'
            })
        }