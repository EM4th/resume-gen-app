#!/usr/bin/env python3
"""
Test script to verify the complete resume content generation
"""

import requests
import json

def test_resume_content():
    print("Testing complete resume content generation...")
    
    # Create a test PDF with clear name and content
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
/Length 200
>>
stream
BT
/F1 12 Tf
50 750 Td
(JOHN SMITH) Tj
0 -20 Td
(555-123-4567 | john@email.com) Tj
0 -30 Td
(EXPERIENCE) Tj
0 -20 Td
(Marketing Assistant, ABC Corp, 2020-2023) Tj
0 -15 Td
(- Created social media content) Tj
0 -15 Td
(- Assisted with campaigns) Tj
0 -15 Td
(- Basic data analysis) Tj
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
450
%%EOF"""
    
    try:
        # Create form data exactly as expected by the endpoint
        files = {
            'resumeFile': ('john_smith_resume.pdf', pdf_content, 'application/pdf')
        }
        data = {
            'jobUrl': 'https://example.com/senior-marketing-manager-job'  # This will fail to scrape, but trigger general optimization
        }
        
        # Make request to local server
        response = requests.post(
            'http://localhost:8080/generate',
            files=files,
            data=data,
            timeout=120
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response keys: {list(result.keys())}")
            
            if 'preview_url' in result:
                pdf_url = result['preview_url']
                print(f"📄 PDF generated: {pdf_url}")
                
                # Try to download and verify the PDF exists
                pdf_response = requests.get(f'http://localhost:8080{pdf_url}')
                print(f"📄 PDF download status: {pdf_response.status_code}")
                print(f"📄 PDF size: {len(pdf_response.content)} bytes")
                
                if len(pdf_response.content) > 1000:
                    print("✅ PDF appears to have substantial content")
                else:
                    print("❌ PDF appears to be too small")
                
            if 'explanation' in result:
                print(f"📋 Explanation preview: {result['explanation'][:200]}...")
                
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_resume_content()
    if success:
        print("\n🎉 Complete resume generation test successful!")
    else:
        print("\n❌ Resume generation test failed")
