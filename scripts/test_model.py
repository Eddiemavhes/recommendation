import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_matcher.settings')
django.setup()

from ml_models.job_matcher import JobMatcher
from cvs.models import CV
from jobs.models import Job

def test_model_loading():
    """Test if the model loads correctly"""
    print("\nTesting model loading...")
    try:
        matcher = JobMatcher()
        print(f"Model path: {matcher.MODEL_PATH}")
        print(f"Model exists: {os.path.exists(matcher.MODEL_PATH)}")
        
        if matcher.model_trained:
            print("✓ Model loaded successfully")
            print(f"Number of jobs in model: {len(matcher.job_listings)}")
            print(f"Number of processed CVs: {len(matcher.cv_processor.processed_cvs)}")
        else:
            print("✗ Model failed to load")
            
    except Exception as e:
        print(f"Error loading model: {str(e)}")

def test_recommendations():
    """Test getting recommendations for existing CVs"""
    print("\nTesting recommendations...")
    matcher = JobMatcher()
    
    # Get all CVs
    cvs = CV.objects.all()
    if not cvs.exists():
        print("No CVs found in database")
        return
    
    print(f"Found {cvs.count()} CVs")
    
    # Test recommendations for first CV
    cv = cvs.first()
    print(f"\nTesting recommendations for CV: {cv.id}")
    
    # First process the CV
    print(f"Processing CV file: {cv.file.path}")
    success = matcher.process_cv(cv.id)
    
    if success:
        print("✓ CV processed successfully")
        # Now get recommendations
        recommendations = matcher.get_job_recommendations(cv.id)
        if recommendations:
            print(f"✓ Got {len(recommendations)} recommendations")
            print("\nTop 3 recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"\n{i}. Job: {rec['title']}")
                print(f"   Company: {rec['company']}")
                if 'match_score' in rec:
                    print(f"   Match Score: {rec['match_score']:.1f}%")
                if 'matching_skills' in rec:
                    print(f"   Matching Skills: {', '.join(rec['matching_skills'])[:100]}")
        else:
            print("✗ No recommendations generated")
    else:
        print("✗ Failed to process CV")

if __name__ == '__main__':
    test_model_loading()
    test_recommendations()