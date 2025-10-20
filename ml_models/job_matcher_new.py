import os
import pickle
import re
from pathlib import Path
import nltk
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
import PyPDF2
import pdfplumber
import io
from .model_classes import SkillsExtractor, CVDataProcessor, RecommendationEngine

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Initialize NLTK resources
STOP_WORDS = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()

class JobMatcher:
    _instance = None
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'trained_models', 'skills_model.pkl')
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating new JobMatcher instance...")
            cls._instance = super(JobMatcher, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        print("Initializing JobMatcher...")
        self.extractor = PDFTextExtractor()
        self.skills_extractor = SkillsExtractor()
        self.recommendation_engine = RecommendationEngine()
        self.model_trained = False
        self.processed_cvs = {}
        self.job_listings = {}
        self._initialized = True
        print("JobMatcher initialization complete.")

    def _load_job_listings(self, search_terms=None):
        """Load job listings from Adzuna API and database"""
        try:
            from jobs.models import Job
            from jobs.services.adzuna_service import AdzunaService
            
            # Initialize Adzuna service
            adzuna = AdzunaService()
            
            # Use provided search terms or default
            if not search_terms:
                search_terms = ['software', 'developer', 'engineer']
            print(f"Searching Adzuna for jobs matching skills: {search_terms}")
            
            # Sync jobs using the service
            jobs_synced = adzuna.sync_jobs(search_terms=search_terms)
            print(f"Synced {jobs_synced} new jobs from Adzuna")
            
            # Now load all jobs from the database
            jobs = Job.objects.all()
            print(f"Loading {len(jobs)} jobs from database...")
            
            for job in jobs:
                # Extract skills from job description
                description_text = f"{job.title}\n{job.description}"
                skills = self.skills_extractor.extract_skills_from_text(description_text)
                
                # Add to job listings
                self.job_listings[job.id] = {
                    'job_id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'description': job.description,
                    'skills': skills,
                    'external_url': job.external_url,
                    'posted_date': job.posted_date,
                    'location': job.location
                }
            
            print(f"Loaded {len(self.job_listings)} jobs successfully")
            self.model_trained = True
            
        except Exception as e:
            print(f"Error loading jobs: {e}")
            self.job_listings = {}
            
    def process_cv(self, cv_id):
        """Process a CV file and return extracted data"""
        if not hasattr(self, 'extractor'):
            print("Re-initializing components...")
            self.extractor = PDFTextExtractor()
            self.skills_extractor = SkillsExtractor()
        
        try:
            # Get CV from database
            from cvs.models import CV
            cv = CV.objects.get(id=cv_id)
            
            # Read file content
            with cv.file.open('rb') as f:
                cv_file = f.read()

            print("\nStarting CV processing...")
            # Extract text from PDF
            text = self.extractor.extract_text(cv_file)
            if not text.strip():
                print("No text extracted from PDF")
                raise ValueError("Could not extract text from PDF")
            
            print(f"Extracted {len(text)} chars of text")
            print("Sample text:", text[:200].replace('\n', ' ') + "...")
            
            # Extract skills from text
            skills = self.skills_extractor.extract_skills_from_text(text)
            print(f"Extracted skills: {skills}")
            
            # Update job listings based on CV skills
            self._load_job_listings(search_terms=skills)
            
            # Store processed CV data
            self.processed_cvs[cv_id] = {
                'text': text,
                'skills': skills,
                'experience_level': self._detect_experience_level(text),
                'years_experience': self._estimate_years_experience(text)
            }
            
            return self.processed_cvs[cv_id]
            
        except Exception as e:
            print(f"Error processing CV: {e}")
            return None
            
    def _detect_experience_level(self, text):
        """Detect experience level from CV text"""
        # Simple rule-based approach
        text = text.lower()
        if 'senior' in text or 'lead' in text or 'manager' in text:
            return 'senior'
        elif 'junior' in text or 'entry' in text or 'graduate' in text:
            return 'junior'
        else:
            return 'mid'
            
    def _estimate_years_experience(self, text):
        """Estimate years of experience from CV text"""
        # Simple heuristic
        text = text.lower()
        years = 0
        experience_patterns = [
            r'(\d+)(?:\+)?\s*(?:year|yr)s?(?:\s+of)?\s+experience',
            r'experience\D*(\d+)(?:\+)?\s*(?:year|yr)s?'
        ]
        
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    years = max(years, int(match.group(1)))
                except (IndexError, ValueError):
                    continue
                    
        return years

    def store_recommendations(self, cv_id, user_id, recommendations):
        """Store job recommendations in the database"""
        from jobs.models import JobRecommendation, Job
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            # Get user
            user = User.objects.get(id=user_id)

            # Delete existing recommendations for this CV and user
            JobRecommendation.objects.filter(user=user, cv_id=cv_id).delete()

            # Store new recommendations
            stored = []
            for rec in recommendations:
                job = Job.objects.get(id=rec['job_id'])
                stored.append(JobRecommendation.objects.create(
                    user=user,
                    job=job,
                    cv_id=cv_id,
                    match_score=rec['match_score'],
                    matching_skills=rec['matching_skills']
                ))
            print(f"Stored {len(stored)} recommendations in database")
            return stored
        except Exception as e:
            print(f"Error storing recommendations: {e}")
            return []

    def get_job_recommendations(self, cv_id, user_id=None, top_k=10):
        """Get job recommendations for a CV"""
        print(f"\nGetting job recommendations for CV {cv_id}")
        print(f"Job listings available: {len(self.job_listings)}")
        
        if not self.job_listings:
            print("No jobs available in the system")
            return []
            
        try:
            recommendations = []
            print(f"Looking for CV {cv_id} in processed CVs...")
            print(f"Available CV IDs: {list(self.processed_cvs.keys())}")
            
            # Process CV if not already processed
            if cv_id not in self.processed_cvs:
                self.process_cv(cv_id)
            
            if cv_id in self.processed_cvs:
                cv_data = self.processed_cvs[cv_id]
                print(f"Found CV data with {len(cv_data.get('skills', []))} skills")
                
                # Use recommendation engine to get matches
                recommendations = self.recommendation_engine.get_recommendations(
                    cv_data=cv_data,
                    job_listings=self.job_listings,
                    top_k=top_k
                )
                
                if recommendations:
                    print(f"✓ Found {len(recommendations)} recommendations")
                    if user_id:
                        # Store recommendations in database
                        stored = self.store_recommendations(cv_id, user_id, recommendations)
                        if stored:
                            print(f"✓ Stored {len(stored)} recommendations in database")
                else:
                    print("No matching jobs found")
                    
            return recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []