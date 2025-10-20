from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import Job, SavedJob
from ml_models.job_matcher import JobMatcher
from cvs.models import CV
import os

@login_required
def recommended_jobs(request):
    from recommendations.models import Recommendation  # Import here to avoid circular imports
    
    # Initialize the job matcher
    matcher = JobMatcher()
    recommendations = []
    
    try:
        # Get user's latest CV
        latest_cv = CV.objects.filter(user=request.user).order_by('-created_at').first()
        
        if latest_cv and latest_cv.extracted_text:
            # Process the CV text
            cv_data = matcher.process_cv(latest_cv.extracted_text)
            
            if cv_data:
                print("CV processed successfully, getting recommendations...")
                # Get job recommendations using CV ID
                recommendations = matcher.get_job_recommendations(latest_cv.id, top_k=20)
                print(f"Got {len(recommendations)} recommendations")
                
                # Convert recommendations to Job objects and save to database
                recommended_jobs = []
                # First, clear old recommendations for this user
                Recommendation.objects.filter(user=request.user).delete()
                
                for rec in recommendations:
                    try:
                        job = Job.objects.get(id=rec['job_id'])
                        # Create or update recommendation
                        recommendation = Recommendation.objects.create(
                            user=request.user,
                            cv=latest_cv,
                            job=job,
                            match_score=rec.get('match_score', 0),
                            content_similarity=rec.get('content_similarity', 0),
                            skills_overlap=rec.get('skill_match_score', 0),
                            experience_compatibility=rec.get('experience_match', 0),
                            category_match=rec.get('category_match', False),
                            matching_skills=rec.get('matching_skills', []),
                            missing_skills=rec.get('missing_skills', []),
                            explanation=f"Matched based on {len(rec.get('matching_skills', []))} skills"
                        )
                        job.match_score = rec.get('match_score', 0)
                        job.skill_match = rec.get('skill_match_score', 0)
                        job.matching_skills = rec.get('matching_skills', [])
                        recommended_jobs.append(job)
                    except Job.DoesNotExist:
                        continue
                    except Exception as e:
                        print(f"Error saving recommendation: {e}")
                
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