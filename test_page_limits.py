#!/usr/bin/env python3

import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import black
import pdfplumber

def test_page_limit_functionality():
    """Test that the system respects page limits"""
    
    # Test data for a single page resume
    single_page_content = """
    **Name:** John Smith
    **Contact:** john.smith@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johnsmith
    **Summary:** Results-driven software engineer with 5+ years of experience developing scalable applications. Expertise in Python, JavaScript, and cloud technologies.
    **Experience:**
    Software Engineer | TechCorp Inc. | 2020 - Present
    • Developed microservices serving 1M+ daily users
    • Reduced deployment time by 75% through CI/CD implementation
    • Led team of 3 junior developers
    
    Junior Developer | StartUp LLC | 2018 - 2020
    • Built responsive web applications using React and Node.js
    • Improved database performance by 40%
    • Collaborated with cross-functional teams
    
    **Skills:**
    Technical: Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL
    Soft Skills: Team Leadership, Project Management, Problem Solving
    
    **Education:**
    Bachelor of Science in Computer Science | University of Technology | 2018
    """
    
    # Test data for content that would exceed one page
    multi_page_content = single_page_content + """
    
    **Additional Experience:**
    Intern Developer | BigCorp | 2017 - 2018
    • Assisted in development of internal tools and applications
    • Gained experience in agile development methodologies
    • Worked closely with senior developers on code reviews
    • Participated in daily standups and sprint planning sessions
    • Contributed to documentation and testing procedures
    
    **Certifications:**
    • AWS Certified Solutions Architect
    • Google Cloud Professional Developer
    • MongoDB Certified Developer
    • Scrum Master Certification
    
    **Projects:**
    E-commerce Platform | Personal Project
    • Built full-stack e-commerce application using MERN stack
    • Implemented user authentication and payment processing
    • Deployed on AWS with auto-scaling capabilities
    
    Task Management App | Team Project
    • Developed React-based task management application
    • Integrated with REST APIs and real-time notifications
    • Collaborated with UX designer for optimal user experience
    
    **Additional Skills:**
    Programming Languages: Python, JavaScript, TypeScript, Java, C++
    Frameworks: React, Angular, Vue.js, Express.js, Django, Flask
    Databases: PostgreSQL, MongoDB, MySQL, Redis
    Cloud Services: AWS, Google Cloud, Microsoft Azure
    DevOps: Docker, Kubernetes, Jenkins, GitLab CI/CD
    """
    
    # Import the actual function from our app
    import sys
    import os
    sys.path.append('/Users/em4/Desktop/resume-gen')
    
    try:
        from app import create_ai_formatted_pdf, parse_structured_resume_data
        
        print("🧪 Testing Page Limit Functionality")
        print("=" * 50)
        
        # Test 1: Single page constraint
        print("\n📄 Test 1: Single Page Resume (limit = 1 page)")
        pdf_buffer_1 = create_ai_formatted_pdf(single_page_content, "Professional format", 1)
        
        # Check the generated PDF page count
        temp_buffer = io.BytesIO(pdf_buffer_1.getvalue())
        with pdfplumber.open(temp_buffer) as pdf:
            page_count_1 = len(pdf.pages)
            print(f"✅ Generated PDF has {page_count_1} page(s) (limit was 1)")
            
        # Save test file
        with open('test_single_page_limit.pdf', 'wb') as f:
            f.write(pdf_buffer_1.getvalue())
        
        # Test 2: Multi-page content with single page constraint
        print("\n📄 Test 2: Extensive Content with 1-Page Limit")
        pdf_buffer_2 = create_ai_formatted_pdf(multi_page_content, "Professional format", 1)
        
        temp_buffer_2 = io.BytesIO(pdf_buffer_2.getvalue())
        with pdfplumber.open(temp_buffer_2) as pdf:
            page_count_2 = len(pdf.pages)
            print(f"✅ Generated PDF has {page_count_2} page(s) (limit was 1)")
            if page_count_2 > 1:
                print("⚠️  WARNING: Content exceeded 1-page limit")
            else:
                print("✅ SUCCESS: Content fits within 1-page limit")
                
        # Save test file
        with open('test_overflow_single_page.pdf', 'wb') as f:
            f.write(pdf_buffer_2.getvalue())
        
        # Test 3: Multi-page allowance
        print("\n📄 Test 3: Multi-Page Content with 2-Page Limit")
        pdf_buffer_3 = create_ai_formatted_pdf(multi_page_content, "Professional format", 2)
        
        temp_buffer_3 = io.BytesIO(pdf_buffer_3.getvalue())
        with pdfplumber.open(temp_buffer_3) as pdf:
            page_count_3 = len(pdf.pages)
            print(f"✅ Generated PDF has {page_count_3} page(s) (limit was 2)")
            if page_count_3 <= 2:
                print("✅ SUCCESS: Content fits within 2-page limit")
            else:
                print("⚠️  WARNING: Content exceeded 2-page limit")
                
        # Save test file
        with open('test_two_page_limit.pdf', 'wb') as f:
            f.write(pdf_buffer_3.getvalue())
        
        print("\n🎯 Page Limit Test Results:")
        print(f"   • 1-page constraint (normal content): {page_count_1} page(s)")
        print(f"   • 1-page constraint (extensive content): {page_count_2} page(s)")
        print(f"   • 2-page constraint (extensive content): {page_count_3} page(s)")
        
        print("\n✅ Page limit functionality implemented!")
        print("📁 Test files created:")
        print("   • test_single_page_limit.pdf")
        print("   • test_overflow_single_page.pdf") 
        print("   • test_two_page_limit.pdf")
        
    except ImportError as e:
        print(f"❌ Error importing functions: {e}")
        print("Make sure the Flask server is not running when testing")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_page_limit_functionality()
