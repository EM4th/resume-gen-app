#!/usr/bin/env python3
"""
Test script to verify the explanation feature is working correctly
"""

import requests
import json

def test_explanation_feature():
    print("Testing the new explanation feature...")
    
    # Create a simple test PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 120
>>
stream
BT
/F1 12 Tf
50 750 Td
(John Smith) Tj
0 -20 Td
(Marketing Assistant) Tj
0 -20 Td
(- Created social media posts) Tj
0 -20 Td
(- Helped with campaigns) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
350
%%EOF"""
    
    try:
        # Create form data exactly as expected by the endpoint
        files = {
            'resumeFile': ('test_resume.pdf', pdf_content, 'application/pdf')
        }
        data = {
            'jobUrl': 'https://www.linkedin.com/jobs/view/123456'  # This will fail to scrape, but that's ok for testing
        }
        
        # Make request to local server with form data
        response = requests.post(
            'http://localhost:8080/generate',
            files=files,
            data=data,
            timeout=120  # Give it more time for AI processing
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response keys: {list(result.keys())}")
            
            if 'explanation' in result:
                print(f"✅ Explanation found!")
                print(f"Explanation content: {result['explanation'][:200]}...")
                return True
            else:
                print("❌ No explanation in response")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_explanation_feature()
    if success:
        print("\n🎉 Explanation feature is working correctly!")
    else:
        print("\n❌ Explanation feature needs debugging")
