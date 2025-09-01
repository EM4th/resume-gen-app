#!/usr/bin/env python3
"""Test DOCX generation functionality"""

import sys
sys.path.append('/Users/em4/Desktop/resume-gen')

from app import create_docx_resume, parse_structured_resume_data

# Test resume data
test_resume_data = """
Name: John Smith
Contact: john.smith@email.com | (555) 123-4567 | New York, NY

Summary: Experienced software engineer with 5+ years developing scalable web applications.

Experience:
Senior Software Engineer | TechCorp | 2020-Present
• Led development of microservices architecture serving 1M+ users
• Implemented CI/CD pipelines reducing deployment time by 60%
• Mentored junior developers and conducted code reviews

Software Engineer | StartupXYZ | 2018-2020
• Built responsive web applications using React and Node.js
• Collaborated with cross-functional teams to deliver features

Skills:
• Programming Languages: Python, JavaScript, Java
• Frameworks: React, Django, Express.js
• Cloud: AWS, Docker, Kubernetes

Education:
Bachelor of Science in Computer Science | University of Technology | 2018
"""

def test_docx_creation():
    print("Testing DOCX creation...")
    
    try:
        docx_buffer = create_docx_resume(test_resume_data, "Professional format")
        
        if docx_buffer:
            # Save to file for testing
            with open('test_resume.docx', 'wb') as f:
                f.write(docx_buffer.getbuffer())
            
            print(f"✅ DOCX created successfully! Size: {docx_buffer.getbuffer().nbytes} bytes")
            print("✅ Saved as 'test_resume.docx'")
            return True
        else:
            print("❌ DOCX creation returned None")
            return False
            
    except Exception as e:
        print(f"❌ Error creating DOCX: {e}")
        return False

if __name__ == "__main__":
    success = test_docx_creation()
    if success:
        print("\n🎉 DOCX generation test passed!")
    else:
        print("\n💥 DOCX generation test failed!")
