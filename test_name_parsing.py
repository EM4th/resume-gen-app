#!/usr/bin/env python3
"""
Test script to verify name parsing is working correctly
"""

def parse_structured_resume_data(resume_data):
    """Parse the structured resume data into sections."""
    sections = {}
    current_section = None
    current_content = []
    first_line_processed = False
    
    lines = resume_data.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Special handling for the first meaningful line - often the name
        if not first_line_processed and not line.lower().startswith(('name:', 'contact:', 'summary:', 'experience:', 'skills:', 'education:', '**')):
            # If first line doesn't look like a section header and looks like a name, treat it as name
            if len(line) < 50 and not line.startswith(('•', '*', '-', '(')) and any(c.isalpha() for c in line):
                sections['name'] = line
                first_line_processed = True
                continue
        
        first_line_processed = True
            
        # Check if this is a section header
        if ':' in line and line.endswith(':'):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            section_name = line[:-1].lower().strip()
            if section_name in ['name', 'contact', 'summary', 'experience', 'skills', 'education']:
                current_section = section_name
                current_content = []
            continue
        elif line.lower().startswith(('name:', 'contact:', 'summary:', 'experience:', 'skills:', 'education:')):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            parts = line.split(':', 1)
            current_section = parts[0].lower().strip()
            current_content = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
            continue
            
        # Add content to current section
        if current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def test_name_parsing():
    print("Testing name parsing...")
    
    # Test case 1: Name at the beginning
    test_data_1 = """Ernest Modarelli
(347) 535-7244 | ernestmodarelli@gmail.com

Summary:
Senior policy advisor with experience...

Experience:
Policy Advisor | 2020-Present
- Led strategic initiatives"""
    
    sections_1 = parse_structured_resume_data(test_data_1)
    print(f"Test 1 - Name found: '{sections_1.get('name', 'NOT FOUND')}'")
    
    # Test case 2: Structured format
    test_data_2 = """**Name:** John Smith
**Contact:** john@email.com
**Summary:** Experienced professional...
**Experience:** Software Engineer | 2019-Present"""
    
    sections_2 = parse_structured_resume_data(test_data_2)
    print(f"Test 2 - Name found: '{sections_2.get('name', 'NOT FOUND')}'")
    
    # Test case 3: Section header format
    test_data_3 = """Name: Jane Doe
Contact: jane@email.com
Summary: Marketing specialist with...
Experience: Marketing Manager | 2021-Present"""
    
    sections_3 = parse_structured_resume_data(test_data_3)
    print(f"Test 3 - Name found: '{sections_3.get('name', 'NOT FOUND')}'")

if __name__ == "__main__":
    test_name_parsing()
