"""Diagnose PDF text extraction by checking CVs in the system."""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_matcher.settings')
import django
django.setup()

import PyPDF2
import pdfplumber
from cvs.models import CV

def check_pdf(path):
    """Try both PDF libraries and report basic info about text extraction."""
    print(f"\nChecking PDF: {path}")
    print(f"File exists: {os.path.exists(path)}")
    try:
        print(f"File size: {os.path.getsize(path)} bytes")
    except Exception as e:
        print(f"Error getting size: {e}")
    
    # Try PyPDF2
    print("\nPyPDF2:")
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"Pages: {len(reader.pages)}")
            text = ""
            for i, page in enumerate(reader.pages, 1):
                t = page.extract_text() or ""
                print(f"Page {i}: {len(t)} chars")
                text += t + "\n"
            print(f"Total text: {len(text.strip())} chars")
            print("First 100 chars:", text[:100].replace('\n', ' '))
    except Exception as e:
        print(f"Error: {e}")
    
    # Try pdfplumber
    print("\npdfplumber:")
    try:
        with pdfplumber.open(path) as pdf:
            print(f"Pages: {len(pdf.pages)}")
            text = ""
            for i, page in enumerate(pdf.pages, 1):
                t = page.extract_text() or ""
                print(f"Page {i}: {len(t)} chars")
                text += t + "\n"
            print(f"Total text: {len(text.strip())} chars")
            print("First 100 chars:", text[:100].replace('\n', ' '))
    except Exception as e:
        print(f"Error: {e}")

def main():
    # First check any existing CVs in the database
    cvs = CV.objects.all()
    if cvs:
        print(f"Found {cvs.count()} CVs in database")
        for cv in cvs:
            try:
                check_pdf(cv.file.path)
            except Exception as e:
                print(f"Error checking CV {cv.id}: {e}")
    else:
        print("No CVs found in database")
    
    # Also check the sample CV in cvs/ folder
    sample = Path('cvs/EDWIN_MAVHENYENGWA_CV.PDF')
    if sample.exists():
        print("\nChecking sample CV file:")
        check_pdf(sample)
    else:
        print("\nNo sample CV found at", sample)
