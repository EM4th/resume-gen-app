#!/usr/bin/env python3

import requests
import json

# Test the aggressive transformation with a basic resume and specific job description
def test_aggressive_transformation():
    url = "http://localhost:8080/generate"
    
    # Mock basic resume data
    basic_resume = """
    John Smith
    john.smith@email.com | 555-123-4567
    
    Summary: Administrative assistant with experience in office work.
    
    Experience:
    Administrative Assistant | ABC Company | 2020-2023
    - Answered phones and emails
    - Filed documents and organized files
    - Helped with basic data entry
    - Assisted manager with various tasks
    
    Sales Associate | XYZ Store | 2018-2020
    - Worked at cash register
    - Helped customers find products
    - Restocked shelves
    - Participated in inventory counts
    
    Skills: Microsoft Office, Customer Service, Filing, Data Entry
    
    Education: High School Diploma | City High School | 2018
    """
    
    # Specific job description for transformation testing
    job_description = """
    Senior Business Operations Analyst
    
    We are seeking a dynamic Senior Business Operations Analyst to join our growing team. 
    
    Key Responsibilities:
    - Lead cross-functional projects to optimize business processes
    - Analyze complex data sets to drive strategic decision-making
    - Develop and maintain sophisticated reporting systems
    - Collaborate with C-level executives on strategic initiatives
    - Manage stakeholder relationships and client communications
    - Drive revenue growth through data-driven insights
    
    Required Qualifications:
    - 3+ years of experience in business analysis or operations
    - Advanced proficiency in Microsoft Excel, PowerBI, and data visualization tools
    - Strong analytical and problem-solving skills
    - Excellent written and verbal communication skills
    - Experience with project management and cross-functional leadership
    - Bachelor's degree preferred
    """
    
    data = {
        'job_description': job_description,
        'resume_text': basic_resume,
        'format': 'pdf'
    }
    
    print("Testing aggressive transformation...")
    print("Original resume has basic titles like 'Administrative Assistant' and 'Sales Associate'")
    print("Target job is 'Senior Business Operations Analyst'")
    print("\nSending request...")
    
    try:
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            print("✅ Resume generated successfully!")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Save the PDF for inspection
            with open('test_aggressive_transformation.pdf', 'wb') as f:
                f.write(response.content)
            print("📄 PDF saved as 'test_aggressive_transformation.pdf'")
            print("\nThe aggressive transformation should show:")
            print("- 'Administrative Assistant' → something like 'Business Operations Coordinator'")
            print("- 'Sales Associate' → something like 'Client Relationship Specialist'")
            print("- Basic tasks transformed into strategic accomplishments")
            print("- Job posting keywords integrated throughout")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_aggressive_transformation()
