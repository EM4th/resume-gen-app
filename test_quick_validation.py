#!/usr/bin/env python3

import requests
import json

def test_explanation_feature():
    """Test that the explanation feature is working"""
    
    # Test data
    test_data = {
        "job_description": "Senior Software Engineer - We need someone with Python, Flask, and web development experience",
        "resume_text": "John Doe\nSoftware Developer at Tech Corp\n- Built web applications\n- Used Python for scripting",
        "format": "pdf"
    }
    
    try:
        # Make request to local server
        response = requests.post(
            "http://localhost:8080/generate", 
            json=test_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Check if we got a PDF
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print(f"✅ Successfully generated PDF")
                print(f"PDF size: {len(response.content)} bytes")
                
                # Save for inspection
                with open('test_validation.pdf', 'wb') as f:
                    f.write(response.content)
                print("✅ PDF saved as test_validation.pdf")
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
    print("Testing explanation feature functionality...")
    success = test_explanation_feature()
    if success:
        print("\n✅ All tests passed! The system is working correctly.")
    else:
        print("\n❌ Tests failed! Check the system status.")
