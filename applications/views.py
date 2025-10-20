from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobApplication
from jobs.models import Job

@login_required
def application_list(request):
    applications = JobApplication.objects.filter(user=request.user)
    return render(request, 'applications/application_list.html', {'applications': applications})

@login_required
def create_application(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    application, created = JobApplication.objects.get_or_create(
        user=request.user,
        job=job,
        defaults={'status': 'applied'}
    )
    if created:
        messages.success(request, 'Application submitted successfully!')
    else:
        messages.info(request, 'You have already applied to this job.')
    return redirect('applications')

@login_required
def update_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        if status in dict(JobApplication.STATUS_CHOICES):
            application.status = status
            application.notes = notes
            application.save()
            messages.success(request, 'Application status updated successfully!')
    return redirect('applications')
