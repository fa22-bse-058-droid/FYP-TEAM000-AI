from django import forms
from .models import CVAnalysis, CVTemplate

class CVUploadForm(forms.ModelForm):
    """Form for uploading CV for analysis"""
    
    class Meta:
        model = CVAnalysis
        fields = ['cv_file']
        widgets = {
            'cv_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'help_text': 'Supported formats: PDF, DOC, DOCX (Max 5MB)'
            })
        }
    
    def clean_cv_file(self):
        """Validate CV file"""
        file = self.cleaned_data.get('cv_file')
        if file:
            allowed_extensions = ['pdf', 'doc', 'docx']
            file_extension = file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                raise forms.ValidationError('Only PDF and DOCX files are allowed.')
            
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('File size must not exceed 5MB.')
        
        return file


class CVComparisonForm(forms.Form):
    """Form for comparing CVs"""
    cv_analysis_1 = forms.ModelChoiceField(
        queryset=CVAnalysis.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='First CV'
    )
    cv_analysis_2 = forms.ModelChoiceField(
        queryset=CVAnalysis.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Second CV'
    )


class CVFilterForm(forms.Form):
    """Form for filtering CV analyses"""
    score_min = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Score'
        })
    )
    score_max = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Score'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('latest', 'Latest'),
            ('highest_score', 'Highest Score'),
            ('lowest_score', 'Lowest Score'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )