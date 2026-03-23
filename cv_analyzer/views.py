from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.utils import timezone
import json
import time
import PyPDF2
from docx import Document

from .models import CVAnalysis, CVFeedback, CVTemplate, KeywordDatabase
from .forms import CVUploadForm, CVComparisonForm, CVFilterForm


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return None


def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return None


def analyze_cv_format(text):
    """Analyze CV format and structure"""
    score = 0
    feedback = []
    
    sections = ['experience', 'education', 'skills', 'summary', 'contact']
    found_sections = sum(1 for section in sections if section.lower() in text.lower())
    
    score += (found_sections / len(sections)) * 25
    
    word_count = len(text.split())
    if 300 <= word_count <= 1000:
        score += 25
        feedback.append("✓ Good CV length (300-1000 words)")
    elif word_count < 300:
        feedback.append("⚠ CV is too short. Aim for 300+ words.")
    else:
        feedback.append("⚠ CV is too long. Try to keep it concise.")
    
    lines = text.split('\n')
    if len(lines) > 10:
        score += 25
        feedback.append("✓ Good structure with multiple sections")
    else:
        feedback.append("⚠ Consider adding more sections for clarity")
    
    if score > 0:
        score += 25
        feedback.append("✓ Basic formatting is good")
    
    return int(score), " ".join(feedback)


def analyze_cv_content(text):
    """Analyze CV content quality"""
    score = 0
    feedback = []
    
    text_lower = text.lower()
    
    action_verbs = ['achieved', 'implemented', 'developed', 'managed', 'led', 'created', 'improved', 'designed', 'built', 'launched']
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    
    if verb_count >= 5:
        score += 30
        feedback.append(f"✓ Great use of action verbs ({verb_count} found)")
    elif verb_count > 0:
        score += 15
        feedback.append(f"⚠ Use more action verbs (found {verb_count}, aim for 5+)")
    else:
        feedback.append("⚠ Missing action verbs. Use words like 'achieved', 'implemented', 'developed'")
    
    if any(char.isdigit() for char in text):
        score += 35
        feedback.append("✓ Good use of metrics and numbers")
    else:
        feedback.append("⚠ Add quantifiable achievements with numbers and percentages")
    
    if len(text) > 500:
        score += 35
        feedback.append("✓ Sufficient content detail")
    else:
        feedback.append("⚠ Add more detailed descriptions of achievements")
    
    return int(score), " ".join(feedback)


def analyze_cv_keywords(text, user):
    """Analyze CV for industry-relevant keywords"""
    score = 0
    feedback = []
    
    job_preference = user.profile.job_preference or "Software Engineer"
    
    try:
        keywords_obj = KeywordDatabase.objects.filter(job_title__icontains=job_preference).first()
        if keywords_obj:
            required_keywords = keywords_obj.get_keywords_list()
            found_keywords = [kw for kw in required_keywords if kw.lower() in text.lower()]
            
            score = int((len(found_keywords) / len(required_keywords)) * 100) if required_keywords else 0
            feedback = f"Found {len(found_keywords)} out of {len(required_keywords)} recommended keywords for '{job_preference}'"
        else:
            score = 50
            feedback = f"No specific keywords found for {job_preference}. Add relevant industry terms."
    except:
        feedback = "Could not analyze keywords"
        score = 0
    
    return score, feedback


def analyze_cv_readability(text):
    """Analyze CV readability"""
    score = 0
    feedback = []
    
    sentences = text.split('.')
    avg_length = len(text.split()) / len(sentences) if sentences else 0
    
    if 10 <= avg_length <= 20:
        score += 30
        feedback.append("✓ Good sentence structure")
    else:
        feedback.append("⚠ Vary sentence length (aim for 10-20 words per sentence)")
    
    paragraphs = text.split('\n\n')
    if len(paragraphs) >= 3:
        score += 35
        feedback.append("✓ Good paragraph structure")
    else:
        feedback.append("⚠ Organize content into clear paragraphs")
    
    if text.count('\n') > 10:
        score += 35
        feedback.append("✓ Well-organized with good formatting")
    else:
        feedback.append("⚠ Use bullet points and line breaks for readability")
    
    return int(score), " ".join(feedback)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def upload_cv_analysis(request):
    """Upload and analyze CV"""
    if request.method == 'POST':
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                start_time = time.time()
                
                cv_analysis = form.save(commit=False)
                cv_analysis.user = request.user
                cv_analysis.save()
                
                file_path = cv_analysis.cv_file.path
                file_extension = cv_analysis.cv_file.name.split('.')[-1].lower()
                
                if file_extension == 'pdf':
                    text = extract_text_from_pdf(file_path)
                elif file_extension in ['doc', 'docx']:
                    text = extract_text_from_docx(file_path)
                else:
                    messages.error(request, 'Unsupported file format')
                    return redirect('upload_cv_analysis')
                
                if not text:
                    messages.error(request, 'Could not extract text from CV')
                    cv_analysis.delete()
                    return redirect('upload_cv_analysis')
                
                format_score, format_feedback = analyze_cv_format(text)
                content_score, content_feedback = analyze_cv_content(text)
                keyword_score, keyword_feedback = analyze_cv_keywords(text, request.user)
                readability_score, readability_feedback = analyze_cv_readability(text)
                
                overall_score = int((format_score + content_score + keyword_score + readability_score) / 4)
                
                cv_analysis.format_score = format_score
                cv_analysis.content_score = content_score
                cv_analysis.keyword_score = keyword_score
                cv_analysis.readability_score = readability_score
                cv_analysis.overall_score = overall_score
                
                cv_analysis.format_feedback = format_feedback
                cv_analysis.content_feedback = content_feedback
                cv_analysis.keyword_feedback = keyword_feedback
                cv_analysis.readability_feedback = readability_feedback
                
                cv_analysis.overall_feedback = f"Your CV scored {overall_score}/100. "
                if overall_score >= 80:
                    cv_analysis.overall_feedback += "Excellent! Your CV is well-structured."
                elif overall_score >= 60:
                    cv_analysis.overall_feedback += "Good start! Review the feedback below to improve."
                else:
                    cv_analysis.overall_feedback += "There's room for improvement. Follow the suggestions to enhance your CV."
                
                cv_analysis.is_analyzed = True
                cv_analysis.analysis_time_taken = time.time() - start_time
                cv_analysis.save()
                
                messages.success(request, 'CV analyzed successfully!')
                return redirect('cv_analysis_detail', pk=cv_analysis.pk)
                
            except Exception as e:
                messages.error(request, f'Error analyzing CV: {str(e)}')
                return redirect('upload_cv_analysis')
    else:
        form = CVUploadForm()
    
    context = {'form': form}
    return render(request, 'cv_analyzer/upload_cv_analysis.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def cv_analysis_list(request):
    """List all CV analyses"""
    analyses = CVAnalysis.objects.filter(user=request.user)
    
    form = CVFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('score_min'):
            analyses = analyses.filter(overall_score__gte=form.cleaned_data['score_min'])
        if form.cleaned_data.get('score_max'):
            analyses = analyses.filter(overall_score__lte=form.cleaned_data['score_max'])
        
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by == 'highest_score':
            analyses = analyses.order_by('-overall_score')
        elif sort_by == 'lowest_score':
            analyses = analyses.order_by('overall_score')
    
    context = {
        'analyses': analyses,
        'form': form
    }
    return render(request, 'cv_analyzer/cv_analysis_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def cv_analysis_detail(request, pk):
    """View detailed CV analysis"""
    analysis = get_object_or_404(CVAnalysis, pk=pk, user=request.user)
    
    context = {
        'analysis': analysis,
        'score_percentage': analysis.overall_score
    }
    return render(request, 'cv_analyzer/cv_analysis_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def cv_comparison(request):
    """Compare two CVs"""
    form = CVComparisonForm()
    form.fields['cv_analysis_1'].queryset = CVAnalysis.objects.filter(user=request.user)
    form.fields['cv_analysis_2'].queryset = CVAnalysis.objects.filter(user=request.user)
    
    comparison_data = None
    
    if 'cv1' in request.GET and 'cv2' in request.GET:
        cv1_id = request.GET.get('cv1')
        cv2_id = request.GET.get('cv2')
        
        try:
            cv1 = CVAnalysis.objects.get(pk=cv1_id, user=request.user)
            cv2 = CVAnalysis.objects.get(pk=cv2_id, user=request.user)
            
            comparison_data = {
                'cv1': cv1,
                'cv2': cv2,
                'format_diff': cv1.format_score - cv2.format_score,
                'content_diff': cv1.content_score - cv2.content_score,
                'keyword_diff': cv1.keyword_score - cv2.keyword_score,
                'readability_diff': cv1.readability_score - cv2.readability_score,
                'overall_diff': cv1.overall_score - cv2.overall_score,
            }
        except CVAnalysis.DoesNotExist:
            messages.error(request, 'One or both CVs not found')
    
    context = {
        'form': form,
        'comparison_data': comparison_data
    }
    return render(request, 'cv_analyzer/cv_comparison.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_cv_analysis(request, pk):
    """Delete CV analysis"""
    analysis = get_object_or_404(CVAnalysis, pk=pk, user=request.user)
    analysis.delete()
    messages.success(request, 'CV analysis deleted successfully!')
    return redirect('cv_analysis_list')


@login_required(login_url='login')
@require_http_methods(["GET"])
def cv_templates(request):
    """View available CV templates"""
    templates = CVTemplate.objects.filter(is_active=True)
    
    context = {
        'templates': templates
    }
    return render(request, 'cv_analyzer/cv_templates.html', context)