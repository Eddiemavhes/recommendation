from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import CV
from ml_models.job_matcher import JobMatcher

@login_required
def upload_cv(request):
    if request.method == 'POST':
        if request.FILES.get('cv'):
            cv_file = request.FILES['cv']
            print(f"Received CV upload: {cv_file.name} ({cv_file.size} bytes)")
            
            # Validate file extension
            if not cv_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Only PDF files are supported.')
                return render(request, 'cvs/upload.html')
            
            try:
                # Initialize job matcher and process CV
                job_matcher = JobMatcher()
                print("JobMatcher initialized")
                
                # Create new CV instance
                cv = CV.objects.create(
                    user=request.user,
                    file=cv_file,
                    is_current=True
                )
                print(f"Created CV record: {cv.id}, file saved at: {cv.file.path}")
                
                # Process the CV using its ID
                success = job_matcher.process_cv(cv.id)
                print(f"CV processing result: {'success' if success else 'failed'}")
                
                if success:
                    # Get the processed CV data
                    cv_data = job_matcher.processed_cvs.get(cv.id)
                    if cv_data:
                        # Update CV instance with extracted data
                        print("Saving extracted data to CV record")
                        cv.extracted_text = cv_data.get('text', '')
                        cv.extracted_skills = cv_data.get('skills', [])
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
