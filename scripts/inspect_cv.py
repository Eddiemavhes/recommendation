"""Diagnose CV text extraction in detail."""
import os
import sys
import traceback
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_matcher.settings')
import django
django.setup()

import io
import PyPDF2
import pdfplumber
import PyPDF2  # Core PDF library
try:
    import fitz  # PyMuPDF - alternative PDF library
except ImportError:
    fitz = None  # Mark as unavailable
from cvs.models import CV

def diagnose_pdf_content(path):
    """Try reading PDF content with multiple libraries."""
    print(f"\nDiagnosing PDF: {path}")
    file_size = os.path.getsize(path)
    print(f"File size: {file_size} bytes")

    # First check if it's really a PDF
    with open(path, 'rb') as f:
        header = f.read(1024)
        print(f"File starts with: {header[:20]}")
        if not header.startswith(b'%PDF'):
            print("WARNING: File does not start with %PDF marker!")
    
    # Try PyPDF2
    print("\n1. PyPDF2:")
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"Pages: {len(reader.pages)}")
            for i, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    print(f"Page {i}: {len(text)} chars")
                    if text:
                        print("Sample:", text[:100].replace('\n', ' ') + "...")
                except Exception as e:
                    print(f"Error extracting page {i}: {e}")
    except Exception as e:
        print(f"PyPDF2 error: {e}")
        traceback.print_exc()
    
    # Try pdfplumber
    print("\n2. pdfplumber:")
    try:
        with pdfplumber.open(path) as pdf:
            print(f"Pages: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text()
                    print(f"Page {i}: {len(text)} chars")
                    if text:
                        print("Sample:", text[:100].replace('\n', ' ') + "...")
                except Exception as e:
                    print(f"Error extracting page {i}: {e}")
    except Exception as e:
        print(f"pdfplumber error: {e}")
        traceback.print_exc()
    
    # Try PyMuPDF if available
    if fitz:
        print("\n3. PyMuPDF:")
        try:
            doc = fitz.open(path)
            print(f"Pages: {doc.page_count}")
            for i, page in enumerate(doc, 1):
                try:
                    text = page.get_text()
                    print(f"Page {i}: {len(text)} chars")
                    if text:
                        print("Sample:", text[:100].replace('\n', ' ') + "...")
                except Exception as e:
                    print(f"Error extracting page {i}: {e}")
            doc.close()
        except Exception as e:
            print(f"PyMuPDF error: {e}")
            traceback.print_exc()

def main():
    # Check recent CVs from database
    print("\nChecking recent CVs from database:")
    cvs = CV.objects.order_by('-created_at')[:5]
    for cv in cvs:
        try:
            print(f"\nCV {cv.id} ({cv.file.name}):")
            diagnose_pdf_content(cv.file.path)
        except Exception as e:
            print(f"Error checking CV {cv.id}: {e}")
    
    # Also check CVs in cvs/ folder
    print("\nChecking CVs in cvs/ folder:")
    cv_dir = Path('cvs')
    for pdf in cv_dir.glob('*.pdf'):
        try:
            diagnose_pdf_content(pdf)
        except Exception as e:
            print(f"Error checking {pdf}: {e}")

if __name__ == '__main__':
    main()