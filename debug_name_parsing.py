#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import parse_structured_resume_data

def test_name_parsing():
    """Test name parsing with different resume formats"""
    
    # Test case 1: Name at the beginning
    test1 = """John Smith
    123 Main St, City, State 12345
    phone: (555) 123-4567
    email: john.smith@email.com
    
    Summary: Experienced professional...
    """
    
    # Test case 2: Structured format
    test2 = """Name: Jane Doe
    Contact: 456 Oak Ave, Town, State 67890
    Summary: Results-driven professional...
    """
    
    # Test case 3: **Name:** format  
    test3 = """**Name:** Bob Johnson
    **Contact:** 789 Pine St, Village, State 13579
    **Summary:** Dynamic leader...
    """
    
    # Test case 4: AI response format
    test4 = """TAILORED_RESUME_DATA:
    **Name:** Alice Wilson
    **Contact:** 321 Elm St, City, State 24680
    **Summary:** Strategic professional...
    """
    
    test_cases = [
        ("Test 1 - Name at beginning", test1),
        ("Test 2 - Structured format", test2), 
        ("Test 3 - **Name:** format", test3),
        ("Test 4 - AI response format", test4)
    ]
    
    for test_name, test_data in test_cases:
        print(f"\n{test_name}:")
        print(f"Input: {test_data[:100]}...")
        
        sections = parse_structured_resume_data(test_data)
        
        if 'name' in sections:
            print(f"✅ Name found: '{sections['name']}'")
        else:
            print("❌ No name found - would default to 'Professional Resume'")
            print("Available sections:", list(sections.keys()))
            if sections:
                print("First few chars of each section:")
                for key, value in sections.items():
                    print(f"  {key}: {value[:50]}...")

if __name__ == "__main__":
    test_name_parsing()
