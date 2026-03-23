from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Job, JobApplication, SavedJob, JobAlert, JobMatchScore, Company
from .forms import JobSearchForm, JobApplicationForm, SaveJobForm, JobAlertForm


@require_http_methods(["GET"])
def job_list(request):
    """List all jobs with search and filter"""
    jobs = Job.objects.filter(status='active')
    
    form = JobSearchForm(request.GET)
    
    if form.is_valid():
        # Keyword search
        keyword = form.cleaned_data.get('keyword')
        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(required_skills__icontains=keyword)
            )
        
        # Location filter
        location = form.cleaned_data.get('location')
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        # Job type filter
        job_types = form.cleaned_data.get('job_type')
        if job_types:
            jobs = jobs.filter(job_type__in=job_types)
        
        # Experience level filter
        exp_levels = form.cleaned_data.get('experience_level')
        if exp_levels:
            jobs = jobs.filter(experience_level__in=exp_levels)
        
        # Salary range filter
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        
        if salary_min:
            jobs = jobs.filter(Q(salary_min__gte=salary_min) | Q(salary_min__isnull=True))
        if salary_max:
            jobs = jobs.filter(Q(salary_max__lte=salary_max) | Q(salary_max__isnull=True))
        
        # Sorting
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by == 'newest':
            jobs = jobs.order_by('-posted_date')
        elif sort_by == 'salary_high':
            jobs = jobs.order_by('-salary_max')
        elif sort_by == 'salary_low':
            jobs = jobs.order_by('salary_min')
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'jobs': jobs_page,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/job_list.html', context)


@require_http_methods(["GET"])
def job_detail(request, pk):
    """View job details"""
    job = get_object_or_404(Job, pk=pk)
    
    # Increment views
    job.views_count += 1
    job.save(update_fields=['views_count'])
    
    # Check if user has applied
    user_applied = False
    if request.user.is_authenticated:
        user_applied = JobApplication.objects.filter(user=request.user, job=job).exists()
    
    # Check if job is saved
    job_saved = False
    if request.user.is_authenticated:
        job_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    
    # Get job match score
    match_score = None
    if request.user.is_authenticated:
        match_score = JobMatchScore.objects.filter(user=request.user, job=job).first()
    
    context = {
        'job': job,
        'user_applied': user_applied,
        'job_saved': job_saved,
        'match_score': match_score,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def apply_job(request, pk):
    """Apply for a job"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if already applied
    existing_application = JobApplication.objects.filter(user=request.user, job=job).first()
    
    if existing_application:
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=job.pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save()
            
            # Update applicants count
            job.applicants_count += 1
            job.save(update_fields=['applicants_count'])
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/apply_job.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def save_job(request, pk):
    """Save a job"""
    job = get_object_or_404(Job, pk=pk)
    
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        messages.info(request, 'Job is already saved.')
    
    return redirect('job_detail', pk=job.pk)


@login_required(login_url='login')
@require_http_methods(["POST"])
def unsave_job(request, pk):
    """Unsave a job"""
    job = get_object_or_404(Job, pk=pk)
    
    SavedJob.objects.filter(user=request.user, job=job).delete()
    messages.success(request, 'Job removed from saved.')
    
    return redirect('job_detail', pk=job.pk)


@login_required(login_url='login')
@require_http_methods(["GET"])
def saved_jobs(request):
    """View saved jobs"""
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
    
    # Pagination
    paginator = Paginator(saved_jobs, 10)
    page_number = request.GET.get('page')
    saved_jobs_page = paginator.get_page(page_number)
    
    context = {
        'saved_jobs': saved_jobs_page,
        'total_saved': saved_jobs.count(),
    }
    return render(request, 'jobs/saved_jobs.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def my_applications(request):
    """View user's job applications"""
    applications = JobApplication.objects.filter(user=request.user).select_related('job')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    applications_page = paginator.get_page(page_number)
    
    context = {
        'applications': applications_page,
        'total_applications': applications.count(),
        'status_filter': status,
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def application_detail(request, pk):
    """View application details"""
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    
    context = {
        'application': application,
        'job': application.job,
    }
    return render(request, 'jobs/application_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_job_alert(request):
    """Create job alert"""
    if request.method == 'POST':
        form = JobAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            messages.success(request, 'Job alert created successfully!')
            return redirect('my_job_alerts')
    else:
        form = JobAlertForm()
    
    context = {
        'form': form,
    }
    return render(request, 'jobs/create_job_alert.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def my_job_alerts(request):
    """View user's job alerts"""
    alerts = JobAlert.objects.filter(user=request.user)
    
    context = {
        'alerts': alerts,
    }
    return render(request, 'jobs/my_job_alerts.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_job_alert(request, pk):
    """Delete job alert"""
    alert = get_object_or_404(JobAlert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, 'Job alert deleted.')
    return redirect('my_job_alerts')


@require_http_methods(["GET"])
def companies(request):
    """List all companies"""
    companies = Company.objects.all()
    
    # Search
    search = request.GET.get('search')
    if search:
        companies = companies.filter(
            Q(name__icontains=search) |
            Q(industry__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(companies, 12)
    page_number = request.GET.get('page')
    companies_page = paginator.get_page(page_number)
    
    context = {
        'companies': companies_page,
        'total_companies': companies.count(),
    }
    return render(request, 'jobs/companies.html', context)


@require_http_methods(["GET"])
def company_detail(request, pk):
    """View company details"""
    company = get_object_or_404(Company, pk=pk)
    jobs = Job.objects.filter(company=company, status='active')
    
    context = {
        'company': company,
        'jobs': jobs,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/company_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def recommended_jobs(request):
    """Get recommended jobs based on user profile"""
    user_profile = request.user.profile
    
    # Get user's job preference and skills
    job_preference = user_profile.job_preference or ""
    skills = user_profile.get_skills_list()
    
    jobs = Job.objects.filter(status='active')
    
    # Filter by job preference
    if job_preference:
        jobs = jobs.filter(
            Q(title__icontains=job_preference) |
            Q(description__icontains=job_preference)
        )
    
    # Score jobs based on skill match
    for job in jobs:
        job_skills = job.get_required_skills_list()
        match_count = sum(1 for skill in job_skills if any(s.lower() in skill.lower() for s in skills))
        job.skill_match_percentage = int((match_count / len(job_skills)) * 100) if job_skills else 0
    
    # Sort by match percentage
    jobs = sorted(jobs, key=lambda x: x.skill_match_percentage, reverse=True)
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    context = {
        'jobs': jobs_page,
    }
    return render(request, 'jobs/recommended_jobs.html', context)