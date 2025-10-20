from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from jobs.models import Job, JobRecommendation
from cvs.models import CV

def home(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    # Get current CV and its recommendations
    current_cv = CV.objects.filter(user=request.user, is_current=True).first()
    recommended_jobs = []
    
    if current_cv:
        recommended_jobs = JobRecommendation.objects.filter(
            user=request.user,
            cv_id=current_cv.id
        ).select_related('job').order_by('-match_score')[:10]
        print(f"Debug: Found {len(recommended_jobs)} recommendations for CV {current_cv.id}")

    context = {
        'current_cv': current_cv,
        'recommended_jobs': recommended_jobs,
        'latest_jobs': Job.objects.all().order_by('-posted_date')[:10],
    }
    return render(request, 'dashboard/dashboard.html', context)
