"""Quick script to simulate uploading a PDF and ensuring processing works.

This script will use the JobMatcher directly to process a PDF file from disk.
Place a sample PDF at scripts/sample_cv.pdf before running.
"""
import os
import sys

# Ensure project root is on sys.path so we can import project modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set Django settings module if available to mirror manage.py environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_matcher.settings')

from ml_models.job_matcher import JobMatcher


if __name__ == '__main__':
    jm = JobMatcher()
    # Prefer a sample in scripts/, otherwise pick the first PDF in cvs/
    from pathlib import Path
    sample = Path('scripts/sample_cv.pdf')
    if not sample.exists():
        cvs_dir = Path('cvs')
        pdfs = list(cvs_dir.glob('*.PDF')) + list(cvs_dir.glob('*.pdf'))
        if pdfs:
            sample = pdfs[0]
            print('Using', sample)
        else:
            print('No sample PDF found in scripts/ or cvs/. Place one to run this test.')
            raise SystemExit(1)

    with open(sample, 'rb') as f:
        data = jm.process_cv(f)
        if data:
            print('Processed OK: ', {k: data.get(k) for k in ['skills', 'experience_level', 'years_experience', 'category']})
        else:
            print('Processing returned None or empty')
