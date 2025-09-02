#!/usr/bin/env python3

import requests
import json

def test_enhanced_transformation():
    """Test the enhanced transformation with gap filling and job description extraction"""
    
    # Test data with employment gaps
    test_data = {
        "job_description": "Senior Data Analyst - Must have Python, SQL, Tableau experience. 5+ years analyzing large datasets. Strong communication skills. Experience with machine learning preferred. Bachelor's degree required.",
        "resume_text": """John Smith
        123 Main St, City, State 12345
        john.smith@email.com | (555) 123-4567
        
        Experience:
        Administrative Assistant - ABC Corp
        January 2020 - March 2021
        - Answered phones and scheduled appointments
        - Filed documents and organized records
        
        Data Entry Clerk - XYZ Company  
        September 2022 - December 2023
        - Entered customer information into database
        - Verified data accuracy
        
        Skills: Microsoft Office, Basic Excel, Customer Service
        Education: Bachelor's Degree in Business, State University, 2019""",
        "format": "pdf"
    }
    
    try:
        # Make request to local server
        response = requests.post(
            "http://localhost:8080/generate", 
            files={
                'resume_file': ('test_resume.txt', test_data['resume_text'], 'text/plain'),
                'job_description': (None, test_data['job_description']),
                'format': (None, test_data['format'])
            },
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if we got a PDF
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print(f"✅ Successfully generated enhanced PDF")
                print(f"PDF size: {len(response.content)} bytes")
                
                # Save for inspection
                with open('test_enhanced_transformation.pdf', 'wb') as f:
                    f.write(response.content)
                print("✅ Enhanced PDF saved as test_enhanced_transformation.pdf")
                
                print("\n🎯 Expected enhancements:")
                print("• Employment gap between March 2021 - September 2022 should be filled")
                print("• Skills should include: Python, SQL, Tableau, Machine Learning")
                print("• Summary should use exact job description language")
                print("• Job titles should be enhanced (e.g., 'Data Analyst' instead of 'Data Entry Clerk')")
                
                return True
            else:
                print(f"❌ Unexpected content type: {content_type}")
                print(f"Response content: {response.text[:500]}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing enhanced transformation with gap filling and job description extraction...")
    success = test_enhanced_transformation()
    if success:
        print("\n✅ Enhanced transformation test completed!")
    else:
        print("\n❌ Enhanced transformation test failed!")
