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
    """Handle CV upload and processing"""
    # Always ensure upload directory exists
    ensure_upload_directory()
    
    if request.method != 'POST':
        return render(request, 'cvs/upload.html')
        
    if not request.FILES.get('cv'):
        messages.error(request, 'No file was uploaded. Please select a CV file.')
        return render(request, 'cvs/upload.html')

    cv_file = request.FILES['cv']
    
    # Validate file size
    if cv_file.size > 5 * 1024 * 1024:  # 5MB limit
        messages.error(request, 'File size too large. Maximum size is 5MB.')
        return render(request, 'cvs/upload.html')
    
    # Validate file type
    if not cv_file.name.lower().endswith('.pdf'):
        messages.error(request, 'Invalid file type. Only PDF files are supported.')
        return render(request, 'cvs/upload.html')

    # Verify PDF content
    try:
        first_bytes = cv_file.read(1024)
        cv_file.seek(0)  # Reset file pointer to beginning
        if not first_bytes.startswith(b'%PDF'):
            messages.error(request, 'The file appears to be corrupted or not a valid PDF.')
            return render(request, 'cvs/upload.html')
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        messages.error(request, 'Unable to read the uploaded file. Please try again.')
        return render(request, 'cvs/upload.html')

    try:
        # Set all previous CVs as not current
        CV.objects.filter(user=request.user, is_current=True).update(is_current=False)
        
        # Create new CV instance
        cv = CV.objects.create(
            user=request.user,
            file=cv_file,
            is_current=True,
            status='uploaded',
            status_message='Processing your CV...',
            progress=0
        )
        
        # Initialize and run job matcher
        job_matcher = JobMatcher()
        success = job_matcher.process_cv(cv.id)
        
        if success:
            cv.status = 'completed'
            cv.status_message = 'CV processed successfully!'
            cv.progress = 100
            cv.save()
            messages.success(request, 'Your CV has been uploaded and processed successfully!')
        else:
            cv.status = 'failed'
            cv.status_message = 'Failed to process CV'
            cv.progress = 0
            cv.save()
            messages.error(request, 'Failed to process your CV. Please try again.')
        
        return redirect('dashboard')
        
    except ValidationError as e:
        print(f"Validation error: {str(e)}")
        messages.error(request, str(e))
        return render(request, 'cvs/upload.html')
    except Exception as e:
        print(f"Error processing CV: {str(e)}")
        messages.error(request, f'Error processing CV: {str(e)}')
        return render(request, 'cvs/upload.html')
                cv = CV.objects.create(
                    user=request.user,
                    file=cv_file,
                    is_current=True,
                    status='uploaded',
                    status_message='CV successfully uploaded, starting analysis...',
                    progress=0,
                    extracted_text='',  # Initialize with empty string
                    extracted_skills=[]  # Initialize with empty list
                )
                print(f"Created new CV record with ID: {cv.id}")
                messages.success(request, 'CV uploaded successfully! Analysis is starting...')
                
                # Initialize job matcher
                try:
                    job_matcher = JobMatcher()
                    print("JobMatcher initialized successfully")
                except Exception as e:
                    print(f"Error initializing JobMatcher: {str(e)}")
                    cv.status = 'failed'
                    cv.status_message = 'Failed to initialize analysis system.'
                    cv.save()
                    messages.error(request, 'Failed to initialize the analysis system. Please try again later.')
                    return redirect('dashboard')
                
                # Update status to processing
                cv.status = 'processing'
                cv.status_message = 'Initializing CV analysis...'
                cv.progress = 10
                cv.save()
                
                # Start text extraction
                cv.status = 'extracting_text'
                cv.status_message = 'Extracting and analyzing CV content...'
                cv.progress = 30
                cv.save()
                
                try:
                    print(f"Starting CV processing for ID: {cv.id}")
                    # Process the CV using its ID
                    success = job_matcher.process_cv(cv.id)
                    print(f"CV processing result: {'success' if success else 'failed'}")
                    
                    if success:
                        try:
                            # Get the processed CV data
                            cv_data = job_matcher.processed_cvs.get(cv.id)
                            if cv_data:
                                cv.extracted_text = cv_data.get('text', '')
                                cv.extracted_skills = cv_data.get('skills', [])
                            cv.status = 'completed'
                            cv.status_message = 'CV analysis completed successfully!'
                            cv.progress = 100
                            cv.save()
                            print(f"CV {cv.id} processed successfully")
                            messages.success(request, 'CV analysis completed! You can now view your job matches.')
                            return redirect('dashboard')
                        except Exception as data_error:
                            print(f"Error saving processed data: {str(data_error)}")
                            raise
                    else:
                        cv.status = 'failed'
                        cv.status_message = 'CV processing failed. Please ensure your PDF is text-searchable and try again.'
                        cv.progress = 0
                        cv.save()
                        messages.error(request, 'CV processing failed. Please ensure your PDF is text-searchable and try again.')
                
                except Exception as e:
                    print(f"Error processing CV: {str(e)}")
                    cv.status = 'error'
                    cv.status_message = f'Error during processing: {str(e)}'
                    cv.progress = 0
                    cv.save()
                    messages.error(request, 'An error occurred during CV processing. Please try again or contact support.')
                
                return redirect('dashboard')
                
            except Exception as outer_error:
                print(f"Outer exception in CV upload: {str(outer_error)}")
                messages.error(request, 'An unexpected error occurred. Please try again or contact support.')
                return redirect('dashboard')
                
    return render(request, 'cvs/upload.html')
                
                if success:
                    # Update status to analyzing skills
                    cv.status = 'analyzing_skills'
                    cv.status_message = 'Analyzing skills from CV...'
                    cv.progress = 60
                    cv.save()
                    
                    # Get the processed CV data
                    cv_data = job_matcher.processed_cvs.get(cv.id)
                    if cv_data:
                        # Update CV instance with extracted data
                        print("Saving extracted data to CV record")
                        cv.extracted_text = cv_data.get('text', '')
                        cv.extracted_skills = cv_data.get('skills', [])
                        cv.status = 'completed'
                        cv.status_message = 'CV analysis completed successfully!'
                        cv.progress = 100
                        cv.save()
                        
                        print(f"Updated CV {cv.id} with data:", {
                            'text_length': len(cv.extracted_text) if cv.extracted_text else 0,
                            'skills': cv.extracted_skills,
                        })
                        
                        # Get and store recommendations
                        recommendations = job_matcher.get_job_recommendations(cv.id, user_id=request.user.id)
                        if recommendations:
                            print(f"Generated and stored {len(recommendations)} recommendations")
                        else:
                            print("No recommendations generated")
                        
                        # Set other CVs as not current
                        CV.objects.filter(user=request.user).exclude(id=cv.id).update(is_current=False)
                        
                        messages.success(request, 'CV uploaded and processed successfully!')
                        return redirect('profile')
                    
                print("CV processing failed - deleting CV record")
                cv.delete()
                messages.error(request, 'CV could not be processed. Please try another PDF.')
                return render(request, 'cvs/upload.html')
                
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error processing CV: {str(e)}')
    
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
