#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path
sys.path.insert(0, '/Users/em4/Desktop/resume-gen')

from app import process_resume_with_ai, extract_text_from_pdf, create_pdf_resume
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_test_pdf():
    """Create a simple test PDF"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=letter)
        styles = getSampleStyleSheet()
        content = [
            Paragraph("John Doe", styles['Title']),
            Paragraph("Software Engineer", styles['Heading1']),
            Paragraph("Experience: 5 years in Python development", styles['Normal']),
            Paragraph("Skills: Python, JavaScript, React", styles['Normal'])
        ]
        doc.build(content)
        return tmp.name

def test_resume_processing():
    """Test the full resume processing pipeline"""
    print("Creating test PDF...")
    test_pdf = create_test_pdf()
    
    try:
        print("Testing PDF text extraction...")
        text = extract_text_from_pdf(test_pdf)
        print(f"Extracted text length: {len(text)}")
        print(f"Extracted text preview: {text[:100]}...")
        
        print("\nTesting resume processing...")
        job_desc = "Looking for a Python developer with React experience"
        output_path = process_resume_with_ai(test_pdf, job_desc, 'pdf')
        
        print(f"Output path: {output_path}")
        print(f"Output file exists: {os.path.exists(output_path)}")
        if os.path.exists(output_path):
            print(f"Output file size: {os.path.getsize(output_path)} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error in processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_pdf):
            os.unlink(test_pdf)

if __name__ == '__main__':
    print("Testing resume generation pipeline...")
    success = test_resume_processing()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")
