#!/usr/bin/env python3
"""
Test script to verify AI explanation and PDF formatting are working
"""

import sys
import os
sys.path.append('/Users/em4/Desktop/resume-gen')

# Test imports
try:
    from app import enhance_resume_with_ai, create_pdf_resume, extract_text_from_pdf
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test AI enhancement
print("\n📝 Testing AI Enhancement...")
try:
    sample_resume = """
John Smith
Email: john.smith@email.com
Phone: (555) 123-4567

EXPERIENCE
Software Developer at Tech Corp
- Developed web applications
- Worked with Python and JavaScript
"""
    
    job_desc = "Python developer with Flask experience and REST API development"
    
    enhanced_content, explanation = enhance_resume_with_ai(sample_resume, job_desc)
    
    print(f"✅ AI Enhancement successful")
    print(f"Enhanced content length: {len(enhanced_content)} characters")
    print(f"Explanation length: {len(explanation)} characters")
    print(f"Explanation preview: {explanation[:200]}...")
    
except Exception as e:
    print(f"❌ AI Enhancement failed: {e}")

# Test PDF creation
print("\n📄 Testing PDF Creation...")
try:
    test_content = """John Smith
Email: john.smith@email.com
Phone: (555) 123-4567

EXPERIENCE
Software Developer at Tech Corp
• Developed web applications using Python and Flask
• Built REST APIs for client applications
• Worked with databases and data management

SKILLS
Python, Flask, JavaScript, SQL"""

    create_pdf_resume(test_content, "test_formatting.pdf")
    print("✅ PDF creation successful")
    
    # Check if file exists and has content
    if os.path.exists("test_formatting.pdf"):
        file_size = os.path.getsize("test_formatting.pdf")
        print(f"PDF file size: {file_size} bytes")
        
        # Test PDF reading
        text = extract_text_from_pdf("test_formatting.pdf")
        print(f"Extracted text length: {len(text)} characters")
        print(f"Text preview: {text[:200]}...")
        
    else:
        print("❌ PDF file not created")
        
except Exception as e:
    print(f"❌ PDF creation failed: {e}")

print("\n🎉 Test completed!")
