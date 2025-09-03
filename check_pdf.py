#!/usr/bin/env python3
"""
Quick script to check the generated PDF quality
"""

import pdfplumber
import sys
import os

def check_pdf_quality(pdf_path):
    """Check if the generated PDF has proper formatting"""
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return False
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"PDF Pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                print(f"\n--- Page {i+1} ---")
                print(text[:500] + "..." if len(text) > 500 else text)
                
        return True
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False

if __name__ == "__main__":
    # Find the most recent generated PDF
    preview_dir = "previews"
    if os.path.exists(preview_dir):
        pdf_files = [f for f in os.listdir(preview_dir) if f.endswith('.pdf')]
        if pdf_files:
            # Get the most recent one
            latest_pdf = max(pdf_files, key=lambda f: os.path.getctime(os.path.join(preview_dir, f)))
            pdf_path = os.path.join(preview_dir, latest_pdf)
            print(f"Checking: {pdf_path}")
            check_pdf_quality(pdf_path)
        else:
            print("No PDF files found in previews directory")
    else:
        print("Previews directory not found")
