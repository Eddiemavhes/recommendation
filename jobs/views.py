from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Job, SavedJob
from .services.adzuna_service import AdzunaService
from ml_models.job_matcher import JobMatcher
from cvs.models import CV

@login_required
def job_list(request):
    # Get query parameters
    query = request.GET.get('q')
    location = request.GET.get('location')
    category = request.GET.get('category')
    job_type = request.GET.get('job_type')
    remote = request.GET.get('remote')

    # Filter jobs
    jobs = Job.objects.all().order_by('-posted_date')
    
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(description__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if category:
        jobs = jobs.filter(category=category)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if remote:
        jobs = jobs.filter(is_remote=True)

    # Sync jobs if requested
    if request.GET.get('sync'):
        adzuna = AdzunaService()
        synced = adzuna.sync_jobs()
        messages.success(request, f'Successfully synced {synced} new jobs!')
        return redirect('job_list')

    # Pagination
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'category': category,
        'job_type': job_type,
        'remote': remote
    })

@login_required
def recommended_jobs(request):
    # Initialize the job matcher
    matcher = JobMatcher()
    recommendations = []
    
    try:
        # Get user's latest CV
        latest_cv = CV.objects.filter(user=request.user).order_by('-created_at').first()
        
        if latest_cv and latest_cv.extracted_text:
            # Get job recommendations and CV data
            recommendations = matcher.get_job_recommendations(latest_cv.id, top_k=20)
            cv_data = matcher.cv_processor.processed_cvs.get(str(latest_cv.id))
            
            # Convert recommendations to Job objects
            recommended_jobs = []
            for rec in recommendations:
                try:
                    job = Job.objects.get(job_id=rec['job_id'])
                    job.match_score = rec['final_score']
                    job.skill_match = rec['skill_match_score']
                    job.matching_skills = rec['matching_skills']
                    recommended_jobs.append(job)
                except Job.DoesNotExist:
                    continue
            
            return render(request, 'jobs/recommended_jobs.html', {
                'jobs': recommended_jobs,
                'cv_data': cv_data,
                'has_recommendations': True
            })
        
        messages.warning(request, 'Upload your CV to get personalized job recommendations!')
        return render(request, 'jobs/recommended_jobs.html', {
            'has_recommendations': False
        })
        
    except Exception as e:
        messages.error(request, 'Error getting job recommendations. Please try again later.')
        return render(request, 'jobs/recommended_jobs.html', {
            'has_recommendations': False,
            'error': str(e)
        })

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        messages.info(request, 'Job was already saved.')
    return redirect('job_detail', job_id=job_id)
