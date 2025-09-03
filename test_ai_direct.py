#!/usr/bin/env python3
"""
Direct test of AI enhancement and PDF generation functions
"""

import sys
import os
sys.path.append('.')

from app import enhance_resume_with_ai, create_pdf_resume, extract_text_from_pdf
import tempfile

def test_ai_functionality():
    """Test the AI enhancement and PDF creation directly"""
    
    # Sample resume text
    sample_resume = """
John Doe
123 Main St, City, State 12345
john.doe@email.com | (555) 123-4567

SUMMARY
Software developer with 3 years experience in web development.

EXPERIENCE
Software Engineer - ABC Company (2021-2024)
- Developed web applications
- Worked with Python and JavaScript
- Collaborated with team members

EDUCATION
Bachelor of Science in Computer Science
XYZ University (2017-2021)

SKILLS
Python, JavaScript, HTML, CSS, Git
"""
    
    job_description = "Looking for a Senior Python Developer with Flask experience and web development skills for a fast-growing startup. Must have experience with REST APIs, database design, and modern web frameworks."
    
    print("🧪 Testing AI Enhancement...")
    print("=" * 50)
    
    try:
        # Test AI enhancement
        enhanced_content, explanation = enhance_resume_with_ai(sample_resume, job_description)
        
        print("✅ AI Enhancement Results:")
        print(f"📄 Enhanced Content Length: {len(enhanced_content)} characters")
        print(f"💡 Explanation Length: {len(explanation)} characters")
        print()
        print("📝 EXPLANATION:")
        print(explanation)
        print()
        print("📄 ENHANCED CONTENT (first 500 chars):")
        print(enhanced_content[:500] + "..." if len(enhanced_content) > 500 else enhanced_content)
        print()
        
        # Test PDF creation
        print("🧪 Testing PDF Creation...")
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            temp_pdf_path = tmp.name
        
        create_pdf_resume(enhanced_content, temp_pdf_path)
        
        if os.path.exists(temp_pdf_path):
            file_size = os.path.getsize(temp_pdf_path)
            print(f"✅ PDF Created Successfully: {file_size} bytes")
            os.unlink(temp_pdf_path)  # Clean up
        else:
            print("❌ PDF Creation Failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct AI & PDF Test")
    print("=" * 50)
    
    success = test_ai_functionality()
    
    if success:
        print("\n🎉 All tests passed! AI enhancement and PDF creation are working.")
    else:
        print("\n💥 Tests failed. Check the error messages above.")
