#!/usr/bin/env python3

import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import black
import pdfplumber

def test_enhanced_page_limits():
    """Test enhanced page limit enforcement for 2-page resumes"""
    
    # Create a test resume with extensive content that would normally go to 3+ pages
    test_resume_data = """
EXPERIENCE:
Senior Software Engineer | ABC Tech Company | 2022 - Present
• Led development of microservices architecture serving 1M+ daily users across 50+ countries
• Implemented CI/CD pipelines reducing deployment time by 75% and increasing team velocity
• Mentored 8 junior developers and conducted 200+ code reviews improving code quality standards
• Collaborated with product teams to deliver customer-focused solutions resulting in 40% user engagement increase
• Architected scalable database solutions handling 10TB+ of data with 99.9% uptime
• Optimized application performance through advanced caching strategies reducing load times by 60%

Software Engineer | XYZ Solutions | 2020 - 2022
• Developed and maintained web applications using React, Node.js, and PostgreSQL for enterprise clients
• Optimized database queries improving application performance by 40% and reducing server costs
• Participated in agile development processes and sprint planning with cross-functional teams
• Created comprehensive documentation for development teams improving onboarding efficiency by 50%
• Implemented automated testing suites achieving 95% code coverage and reducing bugs by 70%
• Built responsive web interfaces serving 500K+ monthly active users

Junior Developer | StartUp Inc | 2018 - 2020
• Built responsive web interfaces using HTML, CSS, JavaScript, and modern frontend frameworks
• Integrated third-party APIs and services including payment gateways and analytics platforms
• Worked closely with design team to implement user interfaces with pixel-perfect accuracy
• Gained experience in version control, collaborative development, and agile methodologies
• Contributed to open-source projects and participated in hackathons winning 2 competitions
• Developed mobile-first applications with React Native serving iOS and Android platforms

Freelance Web Developer | Self-Employed | 2016 - 2018
• Created custom websites and web applications for 20+ small business clients
• Managed full project lifecycle from requirements gathering to deployment and maintenance
• Specialized in e-commerce solutions using WooCommerce and Shopify platforms
• Provided ongoing technical support and training to clients improving their digital presence
• Built SEO-optimized websites resulting in average 200% increase in organic traffic

SKILLS:
Programming Languages: JavaScript, Python, Java, TypeScript, C++, Go, Rust, PHP
Frontend Technologies: React, Vue.js, Angular, HTML5, CSS3, SASS, Bootstrap, Tailwind CSS
Backend Technologies: Node.js, Express.js, Django, Flask, Spring Boot, .NET Core
Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB
Cloud Platforms: AWS, Google Cloud, Azure, Heroku, Vercel, Netlify
DevOps: Docker, Kubernetes, Jenkins, GitLab CI, GitHub Actions, Terraform
"""
    
    # Test with 2-page limit (should compress content to fit)
    original_page_count = 2
    
    sections = {'experience': test_resume_data.split('EXPERIENCE:')[1].split('SKILLS:')[0].strip(),
                'skills': test_resume_data.split('SKILLS:')[1].strip()}
    
    pdf_buffer = io.BytesIO()
    
    # Use enhanced page constraint settings for 2-page limit
    left_margin = 60    # 0.83 inches
    right_margin = 60   
    top_margin = 50     # Tighter top margin
    bottom_margin = 60  # Tighter bottom margin
    base_font_size = 10 # Slightly smaller font
    
    # Create document with page count-appropriate setup
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=letter, 
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )
    
    # Get base styles
    base_styles = getSampleStyleSheet()
    
    # Define compressed styles for 2-page constraint
    section_header_style = ParagraphStyle(
        'SectionHeaderStyle',
        parent=base_styles['Heading2'],
        fontSize=12,  # Smaller for 2-page
        spaceAfter=6,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        textColor=black,
        alignment=TA_LEFT,
        leading=13
    )
    
    job_title_style = ParagraphStyle(
        'JobTitleStyle',
        parent=base_styles['Normal'],
        fontSize=11,
        spaceAfter=1,
        spaceBefore=6,
        fontName='Helvetica-Bold',
        textColor=black,
        alignment=TA_LEFT,
        leading=11
    )
    
    company_date_style = ParagraphStyle(
        'CompanyDateStyle',
        parent=base_styles['Normal'],
        fontSize=10,
        spaceAfter=3,
        spaceBefore=0,
        fontName='Helvetica-Oblique',
        textColor=black,
        alignment=TA_LEFT,
        leading=10
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=base_styles['Normal'],
        fontSize=9,
        spaceAfter=1,
        spaceBefore=0,
        leftIndent=18,
        bulletIndent=8,
        fontName='Helvetica',
        textColor=black,
        alignment=TA_LEFT,
        leading=9
    )
    
    skills_content_style = ParagraphStyle(
        'SkillsContentStyle',
        parent=base_styles['Normal'],
        fontSize=9,
        spaceAfter=3,
        spaceBefore=0,
        fontName='Helvetica',
        textColor=black,
        alignment=TA_LEFT,
        leading=9,
        leftIndent=10
    )
    
    story = []
    
    # Add professional experience with enhanced compression
    experience = sections.get('experience', '')
    if experience:
        story.append(Paragraph('PROFESSIONAL EXPERIENCE', section_header_style))
        
        # Smart parsing of experience content
        exp_lines = [line.strip() for line in experience.split('\n') if line.strip()]
        
        i = 0
        while i < len(exp_lines):
            line = exp_lines[i].replace('**', '').replace('*', '').strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check if this looks like a job entry
            if ('|' in line and ('20' in line or 'Present' in line)) or \
               (any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst'])):
                
                # Create a list to hold all elements of this job entry
                job_elements = []
                
                # This is likely a job title line
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    job_title = parts[0].strip()
                    company_date = ' | '.join(parts[1:]).strip()
                    
                    job_elements.append(Paragraph(job_title, job_title_style))
                    job_elements.append(Paragraph(company_date, company_date_style))
                else:
                    job_elements.append(Paragraph(line, job_title_style))
                
                # Look ahead for bullet points (limit to 3 for space)
                bullet_count = 0
                i += 1
                while i < len(exp_lines) and bullet_count < 3:
                    next_line = exp_lines[i].replace('**', '').replace('*', '').strip()
                    
                    if not next_line:
                        i += 1
                        continue
                    
                    # If it's a bullet point
                    if next_line.startswith(('•', '*', '-')) or \
                       (not next_line.startswith(('**', '#')) and len(next_line) > 20 and not ('|' in next_line and ('20' in next_line or 'Present' in next_line))):
                        
                        # Clean up bullet point
                        bullet_text = next_line
                        for prefix in ['•', '*', '-']:
                            if bullet_text.startswith(prefix):
                                bullet_text = bullet_text[1:].strip()
                                break
                        
                        if bullet_text:
                            job_elements.append(Paragraph(f"• {bullet_text}", bullet_style))
                            bullet_count += 1
                    
                    # If it looks like another job title, break
                    elif ('|' in next_line and ('20' in next_line or 'Present' in next_line)) or \
                         (any(keyword in next_line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst'])):
                        break
                    
                    i += 1
                
                # Add all job elements together as a KeepTogether group
                if job_elements:
                    story.append(KeepTogether(job_elements))
                    # Minimal spacing between jobs
                    story.append(Spacer(1, 4))
                continue
            
            i += 1
    
    # Add skills section - compressed
    skills = sections.get('skills', '')
    if skills:
        story.append(Paragraph('CORE COMPETENCIES', section_header_style))
        
        skill_lines = [line.strip() for line in skills.split('\n') if line.strip()]
        for line in skill_lines:
            line = line.replace('**', '').replace('*', '').strip()
            if line and not line.startswith('#'):
                story.append(Paragraph(line, skills_content_style))
    
    # Build the PDF with page count monitoring
    try:
        doc.build(story)
        pdf_buffer.seek(0)
        
        # Count pages in generated PDF
        temp_pdf_buffer = io.BytesIO(pdf_buffer.getvalue())
        with pdfplumber.open(temp_pdf_buffer) as pdf:
            generated_page_count = len(pdf.pages)
            print(f"DEBUG: Generated PDF has {generated_page_count} pages (limit: {original_page_count})")
            
            if generated_page_count > original_page_count:
                print(f"❌ FAILED: Generated resume exceeded page limit! ({generated_page_count} > {original_page_count})")
                result = "EXCEEDED_LIMIT"
            else:
                print(f"✅ SUCCESS: Generated resume fits within {original_page_count} page(s)")
                result = "WITHIN_LIMIT"
        
        pdf_buffer.seek(0)
        
        # Save test file
        with open('test_2_page_enhanced_limit.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        return result, generated_page_count
        
    except Exception as build_error:
        print(f"Error building PDF: {build_error}")
        return "ERROR", 0

if __name__ == "__main__":
    print("🧪 Testing Enhanced 2-Page Limit Enforcement")
    print("=" * 50)
    
    result, page_count = test_enhanced_page_limits()
    
    print(f"\n📊 Test Results:")
    print(f"   • Result: {result}")
    print(f"   • Generated Pages: {page_count}")
    print(f"   • Page Limit: 2")
    
    if result == "WITHIN_LIMIT":
        print(f"\n✅ Enhanced page limit enforcement is working!")
        print(f"📁 Test file created: test_2_page_enhanced_limit.pdf")
    else:
        print(f"\n❌ Page limit enforcement needs further tuning")
