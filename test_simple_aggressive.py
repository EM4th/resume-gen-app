#!/usr/bin/env python3

import requests
import json
import time

def test_simple_transformation():
    url = "http://localhost:8080/generate"
    
    # Very basic resume
    basic_resume = """John Smith
john@email.com | 555-1234

Summary: Office worker with phone and filing experience.

Experience:
Administrative Assistant | ABC Corp | 2020-2023
- Answered phones
- Filed documents
- Data entry
- Helped manager

Skills: Microsoft Office, Filing, Phone Answering

Education: High School Diploma"""
    
    # Specific job requiring transformation
    job_description = """Senior Business Operations Analyst
    
Key Requirements:
- Advanced data analysis and business intelligence
- Project management and cross-functional leadership  
- Strategic planning and process optimization
- Executive communication and stakeholder management
- Financial modeling and performance metrics
- Bachelor's degree required"""
    
    data = {
        'job_description': job_description,
        'resume_text': basic_resume,
        'format': 'pdf'
    }
    
    print("🔄 Testing AGGRESSIVE transformation...")
    print("📝 Input: Basic 'Administrative Assistant' with phone/filing tasks")
    print("🎯 Target: 'Senior Business Operations Analyst' requiring strategic skills")
    print("\n⏳ Sending request (may take 30-60 seconds for AI processing)...")
    
    try:
        response = requests.post(url, json=data, timeout=120)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Resume generated with aggressive transformation")
            
            # Save the result
            with open('aggressive_transformation_test.pdf', 'wb') as f:
                f.write(response.content)
            
            print("📄 Saved as 'aggressive_transformation_test.pdf'")
            print("\n🎯 Check the PDF to verify aggressive changes:")
            print("   - Job title should be elevated (e.g., 'Business Operations Coordinator')")
            print("   - 'Answered phones' → 'Managed stakeholder communications'")
            print("   - 'Filed documents' → 'Maintained strategic business databases'")
            print("   - 'Data entry' → 'Executed data analysis and reporting'")
            print("   - Skills should emphasize analysis, project management, strategic planning")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Details: {error_data}")
            except:
                print(f"   Response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_simple_transformation()
