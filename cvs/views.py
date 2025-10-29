import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import CV
from ml_models.job_matcher import JobMatcher


def ensure_upload_directory():
    """Ensure the upload directory exists"""
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'cvs')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@login_required
def upload_cv(request):
    """Handle CV upload and processing (single linear flow)."""
    ensure_upload_directory()

    if request.method != 'POST':
        return render(request, 'cvs/upload.html')

    if not request.FILES.get('cv'):
        messages.error(request, 'No file was uploaded. Please select a CV file.')
        return render(request, 'cvs/upload.html')

    cv_file = request.FILES['cv']

    # Validate file size (5MB max)
    if cv_file.size > 5 * 1024 * 1024:
        messages.error(request, 'File size too large. Maximum size is 5MB.')
        return render(request, 'cvs/upload.html')

    # Validate filename extension
    if not cv_file.name.lower().endswith('.pdf'):
        messages.error(request, 'Invalid file type. Only PDF files are supported.')
        return render(request, 'cvs/upload.html')

    # Quick content sniff to confirm PDF header
    try:
        first_bytes = cv_file.read(1024)
        cv_file.seek(0)
        if not isinstance(first_bytes, (bytes, bytearray)) or not first_bytes.startswith(b'%PDF'):
            messages.error(request, 'The file appears to be corrupted or not a valid PDF.')
            return render(request, 'cvs/upload.html')
    except Exception as e:
        print(f"Error reading uploaded file: {e}")
        messages.error(request, 'Unable to read the uploaded file. Please try again.')
        return render(request, 'cvs/upload.html')

    try:
        # Mark other CVs as not current
        CV.objects.filter(user=request.user, is_current=True).update(is_current=False)

        # Create the CV record
        cv = CV.objects.create(
            user=request.user,
            file=cv_file,
            is_current=True,
            status='processing',
            status_message='Processing your CV...',
            progress=10
        )

        # Initialize job matcher and process the CV
        job_matcher = JobMatcher()
        success = job_matcher.process_cv(cv.id)

        if not success:
            cv.status = 'failed'
            cv.status_message = 'CV processing failed.'
            cv.progress = 0
            cv.save()
            messages.error(request, 'Failed to process your CV. Please try again.')
            return render(request, 'cvs/upload.html')

        # Attempt to retrieve processed data (if available)
        try:
            processed = getattr(job_matcher, 'processed_cvs', {})
            cv_data = processed.get(cv.id) if isinstance(processed, dict) else None
        except Exception:
            cv_data = None

        if cv_data:
            cv.extracted_text = cv_data.get('text', '')
            cv.extracted_skills = cv_data.get('skills', [])

        cv.status = 'completed'
        cv.status_message = 'CV processed successfully.'
        cv.progress = 100
        cv.save()
        messages.success(request, 'Your CV has been uploaded and processed successfully!')
        return redirect('dashboard')

    except ValidationError as e:
        print(f"Validation error saving CV: {e}")
        messages.error(request, str(e))
        return render(request, 'cvs/upload.html')
    except Exception as e:
        print(f"Unexpected error processing CV: {e}")
        # Update CV if it exists
        try:
            cv.status = 'failed'
            cv.status_message = f'Error during processing: {e}'
            cv.progress = 0
            cv.save()
        except Exception:
            pass
        messages.error(request, f'Error processing CV: {e}')
        return render(request, 'cvs/upload.html')


@login_required
def update_cv(request):
    if request.method == 'POST':
        cv = CV.objects.filter(user=request.user, is_current=True).first()
        if cv:
            # Update CV data
            cv.save()
            messages.success(request, 'CV information updated successfully!')
            return redirect('profile')
    return redirect('upload_cv')
