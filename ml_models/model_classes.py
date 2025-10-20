from .tech_skills import TECH_SKILLS, EXTRA_TECH_TERMS
import re


class SkillsExtractor:
    def __init__(self):
        # Initialize with technical skills from all categories
        self.skills_keywords = set()
        for category in TECH_SKILLS.values():
            self.skills_keywords.update(skill.lower() for skill in category)
        # Include extra tech terms
        self.skills_keywords.update(term.lower() for term in EXTRA_TECH_TERMS)

        # Add common soft skills
        soft_skills = {
            'teamwork', 'problem solving', 'communication', 'leadership',
            'time management', 'project management', 'analytical', 'customer service',
            'attention to detail', 'organisation', 'organization', 'critical thinking'
        }
        self.skills_keywords.update(soft_skills)

        # Precompile regex patterns for word-boundary matching for each skill
        self.skill_patterns = []
        for skill in sorted(self.skills_keywords, key=lambda s: -len(s)):
            # escape special regex chars and allow optional punctuation between words
            pattern = r'\b' + re.escape(skill) + r'\b'
            self.skill_patterns.append((skill, re.compile(pattern, flags=re.IGNORECASE)))

    def extract_skills_from_text(self, text):
        """Extract both technical and soft skills from text using word-boundary regex matching."""
        found_skills = set()
        for skill, pattern in self.skill_patterns:
            if pattern.search(text):
                found_skills.add(skill)

        # Normalize some variants (e.g., organisation -> organization)
        normalized = set()
        for s in found_skills:
            if s == 'organisation':
                normalized.add('organization')
            else:
                normalized.add(s)

        return sorted(normalized)

class CVDataProcessor:
    def __init__(self):
        self.processed_cvs = {}
        self.skills_extractor = SkillsExtractor()
    
    def process_cv(self, cv_text, cv_id):
        """Process CV text and store the extracted information"""
        # Extract basic information
        cv_data = {
            'id': cv_id,
            'skills': self.skills_extractor.extract_skills_from_text(cv_text),
            'category': 'GENERAL',  # Default category
            'experience_level': 'Entry Level',
            'years_experience': 0
        }
        self.processed_cvs[cv_id] = cv_data
        return cv_data

class RecommendationEngine:
    def __init__(self):
        pass
    
    def get_recommendations(self, cv_data, job_listings, top_k=10):
        """Get job recommendations based on CV data"""
        recommendations = []
        for job_id, job in job_listings.items():
            match_score, matching_skills = self.calculate_match_score(cv_data, job)
            if match_score > 0:
                job_info = {
                    'job_id': job_id,  # Ensure job_id is included
                    'match_score': match_score,
                    'matching_skills': matching_skills
                }
                recommendations.append(job_info)
        
        # Sort by match score and return top k
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:top_k]
    
    def calculate_match_score(self, cv_data, job):
        """Calculate match score between CV and job"""
        # Simple scoring based on skills match
        if 'skills' in cv_data and 'skills' in job:
            cv_skills = set(cv_data['skills'])
            job_skills = set(job['skills'])
            matching_skills = cv_skills.intersection(job_skills)
            if job_skills:
                score = (len(matching_skills) / len(job_skills)) * 100
                return score, list(matching_skills)
        return 0, []