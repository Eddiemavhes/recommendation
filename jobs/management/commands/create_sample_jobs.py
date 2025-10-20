from django.core.management.base import BaseCommand
from jobs.models import Job
from django.utils import timezone
import uuid

SAMPLE_JOBS = [
    {
        'title': 'Junior Python Developer',
        'company': 'TechCorp',
        'location': 'Remote',
        'description': '''Looking for a Junior Python Developer to join our team. 
        You will work on web applications using Django and other modern technologies.
        
        Requirements: Python, Django, HTML/CSS, JavaScript, Git
        
        Technical Skills: Python, Django, HTML, CSS, JavaScript, Git
        Soft Skills: Communication, Problem Solving, Team Work''',
        'category': 'Software Development',
        'job_type': 'full_time',
        'is_remote': True,
        'salary_min': 30000,
        'salary_max': 45000,
    },
    {
        'title': 'Full Stack Developer',
        'company': 'WebSolutions Inc',
        'location': 'Harare',
        'description': '''Full Stack Developer needed for growing startup. 
        Work on exciting projects using modern web technologies.
        
        Requirements: Strong JavaScript skills, React.js, Node.js, Python, MongoDB
        
        Technical Skills: JavaScript, React.js, Node.js, Python, MongoDB, HTML, CSS
        Soft Skills: Problem Solving, Team Work, Communication''',
        'category': 'Software Development',
        'job_type': 'full_time',
        'is_remote': False,
        'salary_min': 45000,
        'salary_max': 65000,
    },
    {
        'title': 'IT Support Specialist',
        'company': 'TechSupport Co',
        'location': 'Harare',
        'description': '''IT Support Specialist needed to provide technical support and troubleshooting for our clients.
        
        Requirements:
        - IT support experience
        - Troubleshooting skills
        - Windows and Linux systems
        - Networking knowledge
        
        Technical Skills: Windows, Linux, Networking, IT Support, Help Desk
        Soft Skills: Customer Service, Communication, Problem Solving''',
        'category': 'IT Support',
        'job_type': 'full_time',
        'is_remote': False,
        'salary_min': 25000,
        'salary_max': 35000,
    },
    {
        'title': 'Web Developer',
        'company': 'Digital Solutions',
        'location': 'Remote',
        'description': '''Web Developer position available for someone passionate about creating great user experiences.
        
        Requirements: HTML5, CSS3, JavaScript, Python, Web Development experience
        
        Technical Skills: HTML5, CSS3, JavaScript, Python, React
        Soft Skills: Creativity, Attention to Detail, Communication''',
        'category': 'Software Development',
        'job_type': 'full_time',
        'is_remote': True,
        'salary_min': 30000,
        'salary_max': 45000,
    },
    {
        'title': 'Security Analyst',
        'company': 'SecureNet',
        'location': 'Harare',
        'description': '''Entry-level Security Analyst position for someone interested in cybersecurity and network protection.
        
        Requirements: 
        - Basic security knowledge
        - Networking fundamentals
        - Linux systems
        - Security monitoring tools
        
        Technical Skills: Security, Networking, Linux, Security Tools
        Soft Skills: Analytical Thinking, Attention to Detail, Communication''',
        'category': 'Information Security',
        'job_type': 'full_time',
        'is_remote': False,
        'salary_min': 35000,
        'salary_max': 50000,
    }
]

class Command(BaseCommand):
    help = 'Creates sample jobs for testing'

    def handle(self, *args, **kwargs):
        # Clear existing jobs
        Job.objects.all().delete()
        
        # Create new jobs
        for job_data in SAMPLE_JOBS:
            # Add required fields
            job_data['job_id'] = str(uuid.uuid4())
            job_data['external_url'] = f"https://example.com/jobs/{job_data['job_id']}"
            job_data['posted_date'] = timezone.now()
            
            # Create the job
            Job.objects.create(**job_data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(SAMPLE_JOBS)} sample jobs'))

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample jobs...')
        
        # Delete existing jobs
        Job.objects.all().delete()
        
        # Create new sample jobs
        for job_data in SAMPLE_JOBS:
            try:
                job = Job.objects.create(
                    job_id=str(uuid.uuid4()),
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    description=job_data['description'].strip(),
                    category=job_data['category'],
                    job_type=job_data['job_type'],
                    is_remote=job_data['is_remote'],
                    salary_min=job_data['salary_min'],
                    salary_max=job_data['salary_max'],
                    external_url=f"https://example.com/jobs/{uuid.uuid4()}",
                    posted_date=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f'Created job: {job.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating job {job_data["title"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully created all sample jobs'))