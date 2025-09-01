import os
import google.generativeai as genai
import re
from flask import Flask, request, jsonify, render_template, send_from_directory
import uuid
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import io
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import black, darkblue
from reportlab.lib.colors import black, darkblue
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# --- Path Definitions ---
PREVIEW_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'previews')
project_root = os.path.dirname(os.path.realpath(__file__))

load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configure Gemini AI ---
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__, template_folder=os.path.join(project_root, 'templates'))
app.config['PREVIEW_FOLDER'] = PREVIEW_FOLDER


# --- Gemini API Configuration ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# --- Helper Functions ---
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF and count original pages"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            page_count = len(pdf.pages)
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            print(f"DEBUG: Original PDF has {page_count} pages")
            return text.strip(), page_count
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        # Default to 1 page if we can't determine
        return f"Could not extract text from PDF: {str(e)}", 1

def scrape_job_description(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        print(f"DEBUG: Scraped text length: {len(text)}")
        print(f"DEBUG: First 500 chars: {text[:500]}")
        
        # Check if we got a login page or insufficient content
        if len(text) < 200 or 'sign in' in text.lower() or 'login' in text.lower():
            print("DEBUG: Detected login page or insufficient content")
            # Return a generic job description request
            return "Please provide a comprehensive job description including: required skills, experience level, responsibilities, and qualifications for the position you're applying to."
        
        return text
        
    except requests.RequestException as e:
        print(f"Error scraping URL: {e}")
        return "Please provide a comprehensive job description including: required skills, experience level, responsibilities, and qualifications for the position you're applying to."

def get_gemini_response(job_description, resume_text, original_page_count=1):
    generation_config = {"temperature": 0.7}
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    
    # Check if we have a real job description or just a placeholder
    has_real_job_desc = not ("Please provide a comprehensive job description" in job_description)
    
    if has_real_job_desc:
        content_instruction = f"""
        STEP 1: AGGRESSIVE JOB-SPECIFIC TRANSFORMATION & PERFECT CANDIDATE POSITIONING
        - COMPLETELY REWRITE the resume to make this person the IDEAL candidate for this specific job
        - AGGRESSIVELY change job titles to match or exceed what the employer is seeking
        - BOLDLY reframe ALL experience to directly align with job requirements 
        - STRATEGICALLY modify company descriptions and roles to highlight relevant industry experience
        - DRAMATICALLY enhance skill descriptions using EXACT terminology from the job posting
        - CREATIVELY reposition past accomplishments to demonstrate perfect job fit
        - EXTENSIVELY use job posting keywords and industry-specific language throughout
        - TRANSFORM mundane tasks into impressive achievements that match job requirements
        - REWRITE summaries to sound like the perfect candidate description for this role
        - BE BOLD: Change titles like "Administrative Assistant" to "Operations Coordinator" if it better matches the target role
        - BE CREATIVE: Reframe "customer service" experience as "client relationship management" for business roles
        - BE STRATEGIC: Emphasize technical skills, leadership experience, or analytical abilities based on what the job demands
        - CRITICAL: Content must fit within {original_page_count} page(s) - the same as the original resume
        """
        
        explanation_instruction = """
        EXPLANATION FOCUS: Describe the aggressive job-specific transformations made including:
        - How job titles were upgraded to match target role requirements
        - How experience was reframed to align with job posting keywords
        - How skills were repositioned to emphasize job requirements
        - How the summary was rewritten to position the candidate as the perfect hire
        - Specific examples of how basic responsibilities became strategic achievements
        """
    else:
        content_instruction = f"""
        STEP 1: AGGRESSIVE PROFESSIONAL ENHANCEMENT & MARKETABILITY MAXIMIZATION
        - COMPLETELY TRANSFORM the resume to create a highly competitive candidate profile
        - BOLDLY upgrade job titles to reflect maximum professional impact and responsibility
        - DRAMATICALLY enhance ALL content to showcase leadership, achievement, and expertise
        - STRATEGICALLY reframe experience to highlight transferable skills and business impact
        - AGGRESSIVELY quantify achievements with impressive metrics and results
        - CREATIVELY position the candidate as an industry expert and high-performer
        - EXTENSIVELY use powerful action verbs and executive-level terminology
        - TRANSFORM basic responsibilities into strategic accomplishments and innovations
        - BE BOLD: Elevate titles and responsibilities to reflect true professional value
        - BE CREATIVE: Reframe experience to showcase leadership, problem-solving, and results
        - BE STRATEGIC: Position candidate as someone who drives growth, efficiency, and success
        - CRITICAL: Content must fit within {original_page_count} page(s) - the same as the original resume
        """
        
        explanation_instruction = """
        EXPLANATION FOCUS: Describe the professional enhancement transformations made including:
        - How job titles were elevated to reflect maximum professional impact
        - How responsibilities were transformed into strategic accomplishments
        - How action verbs and executive terminology improved the presentation
        - How skills were organized and enhanced for better marketability
        - How the overall presentation was upgraded to executive-level standards
        """
    
    prompt = f"""
    You are an elite executive resume strategist with 20+ years creating game-changing resumes that get interviews.
    
    CRITICAL MISSION: AGGRESSIVELY TRANSFORM this resume to create the PERFECT candidate for this specific job.

    {content_instruction}

    STEP 2: STRATEGIC CONTENT TRANSFORMATION GUIDELINES
    - JOB TITLES: Boldly upgrade titles to match target role requirements (e.g., "Assistant" → "Coordinator", "Worker" → "Specialist")
    - COMPANY EXPERIENCE: Strategically reframe companies and roles to highlight relevant industry alignment
    - ACHIEVEMENTS: Dramatically enhance accomplishments with powerful metrics and business impact language
    - SKILLS POSITIONING: Aggressively prioritize and expand skills that directly match job requirements
    - LANGUAGE TRANSFORMATION: Use exact terminology, buzzwords, and phrases from the job posting throughout
    - RESPONSIBILITY ELEVATION: Transform basic tasks into strategic initiatives and leadership opportunities
    - INDUSTRY ALIGNMENT: Reposition experience to demonstrate perfect industry fit and expertise
    
    STEP 3: AGGRESSIVE REWRITING EXAMPLES
    - "Answered phones" → "Managed high-volume client communications and stakeholder relations"
    - "Data entry" → "Maintained critical business databases and ensured data integrity for strategic decision-making"
    - "Team member" → "Collaborative professional contributing to cross-functional team objectives"
    - "Sales associate" → "Client relationship specialist driving revenue growth through consultative sales approach"
    - "Administrative tasks" → "Operational excellence initiatives supporting executive leadership and business efficiency"

    STEP 4: EXACT VISUAL REPLICATION & PROFESSIONAL FORMATTING
    Your task is to create formatting specifications that will produce a resume that:
    - Looks IDENTICAL to the original resume in layout, fonts, spacing, and style
    - Uses professional typography suitable for any corporate environment  
    - Has clean, crisp formatting that will look perfect when printed or viewed digitally
    - Maintains exact visual hierarchy and professional appearance of the original
    - Is immediately ready for job applications without any formatting issues
    - MUST fit within {original_page_count} page(s) exactly - DO NOT exceed this limit

    STEP 5: CONTENT LENGTH OPTIMIZATION
    - Carefully manage content length to fit within {original_page_count} page(s)
    - If original is 1 page, new resume must be 1 page maximum
    - If original is 2 pages, new resume must be 2 pages maximum
    - Prioritize most relevant and impactful content for the target role
    - Use concise, powerful language to maximize impact within space constraints
    - Balance completeness with page limit requirements

    STEP 6: QUALITY ASSURANCE & TRANSFORMATION VALIDATION
    - Ensure transformed content flows naturally and reads authentically
    - Verify ALL changes directly support the target role requirements
    - Check that the candidate now appears to be the IDEAL fit for this position
    - Confirm aggressive changes are believable and professionally appropriate
    - Validate that content fits within the {original_page_count} page limit
    - NEVER include placeholder text like "Enter company name here" or "[Your company]" or similar
    - ALL content must be complete and ready for submission without user editing
    - GUARANTEE: The hiring manager should read this and think "This is EXACTLY who we need!"

    OUTPUT REQUIREMENTS:
    You must provide THREE sections:

    ## TRANSFORMATION_EXPLANATION:
    {explanation_instruction}
    Provide 3-4 bullet points explaining the key improvements made:
    • [Specific transformation example 1]
    • [Specific transformation example 2] 
    • [Specific transformation example 3]
    • [Overall impact statement]

    ## VISUAL_RESUME_IMAGE_DESCRIPTION:
    [Ultra-detailed formatting specifications including:
    - Page setup: exact margins, page size, orientation for {original_page_count} page(s)
    - Typography: specific fonts, sizes, weights for every element
    - Layout: precise spacing, alignment, indentation for all sections
    - Visual hierarchy: how to make headers, subheaders, body text distinct
    - Professional styling: line spacing, paragraph spacing, bullet styles
    - Color scheme: professional colors that work in any business environment
    - Overall appearance: clean, modern, corporate-appropriate design that fits {original_page_count} page(s)]

    ## TAILORED_RESUME_DATA:
    [AGGRESSIVELY TRANSFORMED, job-ready content optimized for {original_page_count} page(s) in this exact structure:
    **Name:** [Original name exactly as provided]
    **Contact:** [Original contact information exactly as provided]
    **Summary:** [COMPLETELY REWRITTEN professional summary that positions candidate as PERFECT for this role - make them sound like the ideal hire]
    **Experience:** [BOLDLY TRANSFORMED jobs with strategically enhanced titles, companies positioned for relevance, dates preserved, and 2-4 powerful bullet points that PROVE perfect job fit]
    **Skills:** [AGGRESSIVELY prioritized and enhanced skills, emphasizing exact job requirements and using posting terminology]
    **Education:** [Education positioned to support target role, enhanced with relevant coursework or achievements if beneficial]
    ]

    CONTEXT FOR AGGRESSIVE CUSTOMIZATION:
    Target Job Description: {job_description}
    
    Original Resume Content: {resume_text}
    
    TRANSFORMATION MANDATE: Be BOLD, be STRATEGIC, be AGGRESSIVE. This resume should make the hiring manager say "We MUST interview this person!" The candidate should appear to be the exact solution to their hiring needs. NO PLACEHOLDER TEXT ALLOWED."""
    
    try:
        response = model.generate_content(prompt)
        print(f"DEBUG: Full Gemini response: {response}")
        if response and response.text:
            return response.text
        else:
            return "Error: AI returned an empty response."
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return "AI generation failed."


def validate_resume_content(resume_data):
    """Validate resume content to ensure no placeholder text exists and content is sufficiently transformed."""
    placeholder_patterns = [
        'enter company name here',
        'company name here',
        '[company name]',
        '[your company]',
        '[insert company]',
        'your company name',
        'add company name',
        '[enter',
        '[add',
        '[insert',
        'placeholder',
        'fill in',
        'todo',
        'tbd',
        'to be determined',
        '[date]',
        '[year]',
        'enter date',
        'add date'
    ]
    
    # Check for generic/weak language that indicates insufficient transformation
    weak_language_patterns = [
        'responsible for',
        'duties included',
        'worked on',
        'helped with',
        'assisted in',
        'participated in',
        'involved in',
        'basic',
        'simple',
        'general'
    ]
    
    resume_lower = resume_data.lower()
    found_placeholders = []
    found_weak_language = []
    
    for pattern in placeholder_patterns:
        if pattern in resume_lower:
            found_placeholders.append(pattern)
    
    for pattern in weak_language_patterns:
        if pattern in resume_lower:
            found_weak_language.append(pattern)
    
    # Return both placeholder issues and weak language warnings
    return found_placeholders, found_weak_language

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import black, darkblue


def parse_ai_response(ai_response):
    """Parse the AI response to extract transformation explanation, visual description and structured resume data."""
    try:
        # Look for the transformation explanation, visual description and structured data
        if "TRANSFORMATION_EXPLANATION:" in ai_response and "VISUAL_RESUME_IMAGE_DESCRIPTION:" in ai_response and "TAILORED_RESUME_DATA:" in ai_response:
            parts = ai_response.split("VISUAL_RESUME_IMAGE_DESCRIPTION:")
            explanation_section = parts[0].replace("TRANSFORMATION_EXPLANATION:", "").strip()
            
            remaining_parts = parts[1].split("TAILORED_RESUME_DATA:")
            visual_description = remaining_parts[0].strip()
            resume_data = remaining_parts[1].strip()
            
            return resume_data, visual_description, explanation_section
            
        # Look for the older format with visual description and structured data only
        elif "VISUAL_RESUME_IMAGE_DESCRIPTION:" in ai_response and "TAILORED_RESUME_DATA:" in ai_response:
            parts = ai_response.split("TAILORED_RESUME_DATA:")
            visual_description = parts[0].replace("VISUAL_RESUME_IMAGE_DESCRIPTION:", "").strip()
            resume_data = parts[1].strip()
            
            # Generate a basic explanation since none was provided
            explanation_section = """
            • Professional formatting and layout optimization for maximum visual impact
            • Enhanced content structure with improved readability and flow
            • Strategic content positioning to highlight key qualifications and achievements
            • Overall presentation upgraded to executive-level professional standards
            """
            
            return resume_data, visual_description, explanation_section
            
        # Fallback to old format if AI uses it
        elif "COMPLETE_TAILORED_RESUME:" in ai_response and "VISUAL_FORMATTING_SPEC:" in ai_response:
            parts = ai_response.split("VISUAL_FORMATTING_SPEC:")
            content_section = parts[0].replace("COMPLETE_TAILORED_RESUME:", "").strip()
            formatting_section = parts[1].strip()
            
            # Extract just the resume content
            lines = content_section.split('\n')
            resume_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.endswith(']'):
                    resume_lines.append(line)
            
            complete_resume = '\n'.join(resume_lines)
            
            # Generate basic explanation
            explanation_section = """
            • Content enhanced with professional language and action-oriented descriptions
            • Experience section restructured for maximum impact and readability
            • Skills section organized to highlight most relevant qualifications
            • Overall presentation improved to meet current industry standards
            """
            
            return complete_resume, formatting_section, explanation_section
            
        else:
            # If AI doesn't follow format, treat entire response as resume content
            print("DEBUG: AI didn't follow expected format, using entire response as resume")
            explanation_section = """
            • Resume content has been enhanced and professionally formatted
            • Content structure improved for better readability and impact
            • Professional presentation standards applied throughout
            • Resume optimized for modern application tracking systems
            """
            return ai_response, "Use professional formatting", explanation_section
            
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        explanation_section = """
        • Resume has been processed and formatted for professional presentation
        • Content enhanced to improve overall impact and readability
        • Professional standards applied to layout and structure
        • Resume prepared for immediate use in job applications
        """
        return ai_response, "Use professional formatting", explanation_section


def create_resume_image_from_description(resume_data, visual_description):
    """Create a visual resume image based on the AI's detailed description and structured data."""
    # Parse the structured resume data
    resume_sections = parse_structured_resume_data(resume_data)
    
    # Create image dimensions (8.5" x 11" at 300 DPI)
    width, height = 2550, 3300  # 300 DPI
    
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts, fallback to default if not available
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)  # Name
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)  # Section headers
        font_normal = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)  # Regular text
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)   # Contact info
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Starting position
    y_pos = 100
    margin = 150
    line_height = 40
    
    # Draw name (centered, large, bold)
    if 'name' in resume_sections:
        name = resume_sections['name']
        name_bbox = draw.textbbox((0, 0), name, font=font_large)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (width - name_width) // 2
        draw.text((name_x, y_pos), name, fill='black', font=font_large)
        y_pos += 80
    
    # Draw contact info (centered, smaller)
    if 'contact' in resume_sections:
        contact_lines = resume_sections['contact'].split('\n')
        for contact_line in contact_lines:
            if contact_line.strip():
                contact_bbox = draw.textbbox((0, 0), contact_line, font=font_small)
                contact_width = contact_bbox[2] - contact_bbox[0]
                contact_x = (width - contact_width) // 2
                draw.text((contact_x, y_pos), contact_line, fill='black', font=font_small)
                y_pos += 35
        y_pos += 30
    
    # Draw sections (Summary, Experience, Skills, Education)
    sections_order = ['summary', 'experience', 'skills', 'education']
    
    for section_key in sections_order:
        if section_key in resume_sections and resume_sections[section_key]:
            # Section header
            section_title = section_key.upper()
            draw.text((margin, y_pos), section_title, fill='black', font=font_medium)
            y_pos += 50
            
            # Section content
            content = resume_sections[section_key]
            
            if section_key == 'experience':
                # Handle experience with job titles and bullets
                jobs = content.split('\n\n')  # Assume jobs are separated by double newlines
                for job in jobs:
                    if job.strip():
                        lines = job.strip().split('\n')
                        for i, line in enumerate(lines):
                            if line.strip():
                                if i == 0:  # Job title (bold)
                                    draw.text((margin, y_pos), line, fill='black', font=font_normal)
                                elif line.strip().startswith(('•', '*', '-')):  # Bullet points
                                    # Wrap long bullet points
                                    bullet_text = line.strip()[1:].strip()
                                    wrapped_lines = textwrap.wrap(bullet_text, width=80)
                                    for j, wrapped_line in enumerate(wrapped_lines):
                                        if j == 0:
                                            draw.text((margin + 30, y_pos), f"• {wrapped_line}", fill='black', font=font_normal)
                                        else:
                                            draw.text((margin + 50, y_pos), wrapped_line, fill='black', font=font_normal)
                                        y_pos += line_height
                                    continue
                                else:  # Company name (italic)
                                    draw.text((margin, y_pos), line, fill='black', font=font_normal)
                                y_pos += line_height
                        y_pos += 20  # Space between jobs
            else:
                # Handle other sections
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        if ':' in line and section_key == 'skills':
                            # Skills with categories
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                category = parts[0].strip()
                                skills = parts[1].strip()
                                # Draw category in bold
                                draw.text((margin, y_pos), f"{category}:", fill='black', font=font_normal)
                                # Draw skills
                                draw.text((margin + 200, y_pos), skills, fill='black', font=font_normal)
                        else:
                            # Wrap long lines
                            wrapped_lines = textwrap.wrap(line, width=85)
                            for wrapped_line in wrapped_lines:
                                draw.text((margin, y_pos), wrapped_line, fill='black', font=font_normal)
                                y_pos += line_height
                            continue
                        y_pos += line_height
            
            y_pos += 30  # Space between sections
    
    return img


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
        elif line.startswith('**') and ':' in line and line.endswith('**'):
            # Handle **Name:** format
            section_line = line.replace('**', '').strip()
            if section_line.lower().startswith(('name:', 'contact:', 'summary:', 'experience:', 'skills:', 'education:')):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                parts = section_line.split(':', 1)
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


def create_fallback_text_pdf(resume_data):
    """Fallback function to create a simple text-based PDF if image creation fails."""
    pdf_buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=letter, 
        leftMargin=72,
        rightMargin=72, 
        topMargin=72, 
        bottomMargin=72
    )
    
    base_styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle(
        'NameStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=black
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        spaceAfter=6
    )
    
    story = []
    lines = [line.strip() for line in resume_data.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        if i == 0:  # First line is likely the name
            story.append(Paragraph(line, name_style))
        else:
            story.append(Paragraph(line, normal_style))
    
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer


def create_ai_formatted_pdf(resume_data, visual_description, original_page_count=1):
    """Create a professionally formatted, job-ready resume PDF that respects the original page count."""
    try:
        # Parse the resume data into structured sections
        sections = parse_structured_resume_data(resume_data)
        
        pdf_buffer = io.BytesIO()
        
        # Adjust margins and spacing based on page count constraint
        if original_page_count == 1:
            # Very tight margins and spacing for 1-page constraint
            left_margin = 54    # 0.75 inches
            right_margin = 54   
            top_margin = 45     # Very tight top margin
            bottom_margin = 54  # Very tight bottom margin
            base_font_size = 9  # Smaller font for more content
            space_after_section = 6
        elif original_page_count == 2:
            # Moderately tight margins for 2-page constraint
            left_margin = 60    # 0.83 inches
            right_margin = 60   
            top_margin = 50     # Tighter top margin
            bottom_margin = 60  # Tighter bottom margin
            base_font_size = 10 # Slightly smaller font
            space_after_section = 8
        else:
            # Standard professional margins for 3+ pages
            left_margin = 72    # 1 inch - professional standard
            right_margin = 72   
            top_margin = 60     
            bottom_margin = 72  
            base_font_size = 11
            space_after_section = 12
        
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
        
        # Define professional corporate-ready styles (responsive to page count)
        name_style = ParagraphStyle(
            'NameStyle',
            parent=base_styles['Heading1'],
            fontSize=18 if original_page_count == 1 else (20 if original_page_count == 2 else 22),
            spaceAfter=3 if original_page_count <= 2 else 6,
            spaceBefore=0,
            alignment=TA_CENTER,   # Clean centered look
            textColor=black,
            fontName='Helvetica-Bold',
            leading=20 if original_page_count == 1 else (22 if original_page_count == 2 else 26)
        )
        
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=base_styles['Normal'],
            fontSize=9 if original_page_count == 1 else (10 if original_page_count == 2 else 11),
            spaceAfter=8 if original_page_count == 1 else (10 if original_page_count == 2 else 16),
            alignment=TA_CENTER,
            textColor=black,
            fontName='Helvetica',
            leading=10 if original_page_count == 1 else (11 if original_page_count == 2 else 13)
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeaderStyle',
            parent=base_styles['Heading2'],
            fontSize=11 if original_page_count == 1 else (12 if original_page_count == 2 else 13),
            spaceAfter=4 if original_page_count == 1 else (6 if original_page_count == 2 else 8),
            spaceBefore=12 if original_page_count == 1 else (14 if original_page_count == 2 else 18),
            fontName='Helvetica-Bold',
            textColor=black,
            alignment=TA_LEFT,
            borderPadding=0,
            leading=12 if original_page_count == 1 else (13 if original_page_count == 2 else 15),
            # Add professional underline separator
            borderWidth=0,
            borderColor=black,
            leftIndent=0
        )
        
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size,
            spaceAfter=4 if original_page_count <= 2 else 8,
            spaceBefore=2 if original_page_count <= 2 else 4,
            fontName='Helvetica',
            textColor=black,
            alignment=TA_LEFT,
            leading=10 if original_page_count == 1 else (11 if original_page_count == 2 else 14),
            leftIndent=0
        )
        
        job_title_style = ParagraphStyle(
            'JobTitleStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size + 1,
            spaceAfter=1 if original_page_count <= 2 else 3,
            spaceBefore=4 if original_page_count == 1 else (6 if original_page_count == 2 else 8),
            fontName='Helvetica-Bold',
            textColor=black,
            alignment=TA_LEFT,
            leading=10 if original_page_count == 1 else (11 if original_page_count == 2 else 14)
        )
        
        company_date_style = ParagraphStyle(
            'CompanyDateStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size,
            spaceAfter=2 if original_page_count == 1 else (3 if original_page_count == 2 else 6),
            spaceBefore=0,
            fontName='Helvetica-Oblique',
            textColor=black,
            alignment=TA_LEFT,
            leading=9 if original_page_count == 1 else (10 if original_page_count == 2 else 13)
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size - 1,
            spaceAfter=1 if original_page_count <= 2 else 4,
            spaceBefore=0,
            leftIndent=18,
            bulletIndent=8,
            fontName='Helvetica',
            textColor=black,
            alignment=TA_LEFT,
            leading=8 if original_page_count == 1 else (9 if original_page_count == 2 else 12)
        )
        
        skills_header_style = ParagraphStyle(
            'SkillsHeaderStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size,
            spaceAfter=2 if original_page_count <= 2 else 4,
            spaceBefore=3 if original_page_count <= 2 else 6,
            fontName='Helvetica-Bold',
            textColor=black,
            alignment=TA_LEFT,
            leading=9 if original_page_count == 1 else (10 if original_page_count == 2 else 13)
        )
        
        skills_content_style = ParagraphStyle(
            'SkillsContentStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size - 1,
            spaceAfter=2 if original_page_count == 1 else (3 if original_page_count == 2 else 6),
            spaceBefore=0,
            fontName='Helvetica',
            textColor=black,
            alignment=TA_LEFT,
            leading=8 if original_page_count == 1 else (9 if original_page_count == 2 else 12),
            leftIndent=10
        )
        
        education_style = ParagraphStyle(
            'EducationStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size,
            spaceAfter=1 if original_page_count <= 2 else 4,
            spaceBefore=1 if original_page_count <= 2 else 4,
            fontName='Helvetica',
            textColor=black,
            alignment=TA_LEFT,
            leading=9 if original_page_count == 1 else (10 if original_page_count == 2 else 13)
        )
        
        story = []
        
        # Add name - clean and professional with better fallback
        name = sections.get('name', '')
        if not name.strip():
            # Try to extract name from the first line of resume data if name section is empty
            resume_lines = [line.strip() for line in resume_data.split('\n') if line.strip()]
            for line in resume_lines:
                # Skip section headers and look for a name-like line
                if not line.lower().startswith(('name:', 'contact:', 'summary:', 'experience:', 'skills:', 'education:', '**', '#')):
                    # Check if it looks like a name (has letters, not too long, not bullet points)
                    if len(line) < 50 and not line.startswith(('•', '*', '-', '(')) and any(c.isalpha() for c in line):
                        name = line
                        break
            
            # Final fallback if still no name found
            if not name.strip():
                name = 'Professional Resume'
        
        clean_name = name.replace('**', '').replace('*', '').strip()
        story.append(Paragraph(clean_name, name_style))
        
        # Add contact information - professional formatting
        contact = sections.get('contact', '')
        if contact:
            clean_contact = contact.replace('**', '').replace('*', '').strip()
            # Format contact info cleanly
            contact_lines = [line.strip() for line in clean_contact.split('\n') if line.strip()]
            if contact_lines:
                # Join contact info with clean separators
                formatted_contact = ' | '.join(contact_lines)
                story.append(Paragraph(formatted_contact, contact_style))
        
        # Add professional summary with section grouping
        summary = sections.get('summary', '')
        if summary:
            summary_section = []
            # Add section header with professional styling
            summary_section.append(Paragraph('PROFESSIONAL SUMMARY', section_header_style))
            # Add subtle separator line for professionalism
            from reportlab.platypus import HRFlowable
            summary_section.append(HRFlowable(width="100%", thickness=0.5, color=black, spaceAfter=6))
            
            clean_summary = summary.replace('**', '').replace('*', '').strip()
            summary_paragraphs = [p.strip() for p in clean_summary.split('\n') if p.strip()]
            for para in summary_paragraphs:
                summary_section.append(Paragraph(para, summary_style))
            # Keep entire summary section together
            story.append(KeepTogether(summary_section))
            story.append(Spacer(1, space_after_section))
        
        # Add professional experience - formatted for readability with page break protection
        experience = sections.get('experience', '')
        if experience:
            # Add section header with professional styling
            story.append(Paragraph('PROFESSIONAL EXPERIENCE', section_header_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=black, spaceAfter=8))
            
            # Smart parsing of experience content
            exp_lines = [line.strip() for line in experience.split('\n') if line.strip()]
            
            i = 0
            while i < len(exp_lines):
                line = exp_lines[i].replace('**', '').replace('*', '').strip()
                
                # Skip empty lines and markdown
                if not line or line.startswith('#'):
                    i += 1
                    continue
                
                # Check if this looks like a job entry (has dates or company indicators)
                if ('|' in line and ('20' in line or 'Present' in line)) or \
                   (any(keyword in line.lower() for keyword in ['manager', 'director', 'analyst', 'specialist', 'coordinator', 'assistant', 'associate', 'senior', 'junior', 'lead'])):
                    
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
                    
                    # Look ahead for company/date info and bullet points
                    i += 1
                    while i < len(exp_lines):
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
                            
                            if bullet_text:  # Only add non-empty bullets
                                job_elements.append(Paragraph(f"• {bullet_text}", bullet_style))
                        
                        # If it looks like another job title, break
                        elif ('|' in next_line and ('20' in next_line or 'Present' in next_line)) or \
                             (any(keyword in next_line.lower() for keyword in ['manager', 'director', 'analyst', 'specialist', 'coordinator', 'assistant', 'associate', 'senior', 'junior', 'lead'])):
                            break
                        
                        # If it's company/date info for current job
                        elif '20' in next_line or 'Present' in next_line:
                            job_elements.append(Paragraph(next_line, company_date_style))
                        
                        i += 1
                    
                    # Add all job elements together as a KeepTogether group to prevent page breaks
                    if job_elements:
                        story.append(KeepTogether(job_elements))
                        # Add spacing between jobs
                        story.append(Spacer(1, 6))
                    continue
                
                i += 1
        
        # Add skills section - well organized and kept together
        skills = sections.get('skills', '')
        if skills:
            skills_section = []
            skills_section.append(Paragraph('CORE COMPETENCIES', section_header_style))
            skills_section.append(HRFlowable(width="100%", thickness=0.5, color=black, spaceAfter=6))
            
            skill_lines = [line.strip() for line in skills.split('\n') if line.strip()]
            for line in skill_lines:
                line = line.replace('**', '').replace('*', '').strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        # Category: skills format
                        parts = line.split(':', 1)
                        category = parts[0].strip()
                        skills_list = parts[1].strip()
                        
                        skills_section.append(Paragraph(f"<b>{category}:</b>", skills_header_style))
                        skills_section.append(Paragraph(skills_list, skills_content_style))
                    else:
                        skills_section.append(Paragraph(line, skills_content_style))
            
            # Keep entire skills section together
            story.append(KeepTogether(skills_section))
            story.append(Spacer(1, space_after_section))
        
        # Add education - clean formatting and kept together
        education = sections.get('education', '')
        if education:
            education_section = []
            education_section.append(Paragraph('EDUCATION', section_header_style))
            education_section.append(HRFlowable(width="100%", thickness=0.5, color=black, spaceAfter=6))
            
            edu_lines = [line.strip() for line in education.split('\n') if line.strip()]
            for line in edu_lines:
                line = line.replace('**', '').replace('*', '').strip()
                if line and not line.startswith('#'):
                    education_section.append(Paragraph(line, education_style))
            
            # Keep entire education section together
            story.append(KeepTogether(education_section))
        
        # Build the PDF with page count monitoring
        try:
            doc.build(story)
            pdf_buffer.seek(0)
            
            # Quick check: count pages in generated PDF
            temp_pdf_buffer = io.BytesIO(pdf_buffer.getvalue())
            with pdfplumber.open(temp_pdf_buffer) as pdf:
                generated_page_count = len(pdf.pages)
                print(f"DEBUG: Generated PDF has {generated_page_count} pages (limit: {original_page_count})")
                
                if generated_page_count > original_page_count:
                    print(f"WARNING: Generated resume exceeded page limit! ({generated_page_count} > {original_page_count})")
                    # Attempt to create a more compressed version
                    return create_compressed_pdf(resume_data, visual_description, original_page_count)
                else:
                    print(f"SUCCESS: Generated resume fits within {original_page_count} page(s)")
            
            pdf_buffer.seek(0)
            return pdf_buffer
            
        except Exception as build_error:
            print(f"Error building PDF: {build_error}")
            raise build_error
        
    except Exception as e:
        print(f"Error creating professional PDF: {e}")
        print(f"DEBUG: Falling back to simple text PDF due to error: {type(e).__name__}")
        # Fallback to simple text PDF
        return create_fallback_text_pdf(resume_data)
    

def create_compressed_pdf(resume_data, visual_description, original_page_count):
    """Create an ultra-compressed PDF when the original exceeds page limits."""
    try:
        print(f"DEBUG: Creating compressed version for {original_page_count} page limit")
        sections = parse_structured_resume_data(resume_data)
        
        pdf_buffer = io.BytesIO()
        
        # Ultra-tight constraints for compression
        if original_page_count == 1:
            left_margin = 45    # 0.625 inches - very tight
            right_margin = 45   
            top_margin = 40     
            bottom_margin = 45  
            base_font_size = 8  # Very small font
        elif original_page_count == 2:
            left_margin = 50    # 0.69 inches - tight
            right_margin = 50   
            top_margin = 40     
            bottom_margin = 50  
            base_font_size = 9  # Small font
        else:
            left_margin = 60
            right_margin = 60
            top_margin = 50
            bottom_margin = 60
            base_font_size = 10
        
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter, 
            leftMargin=left_margin,
            rightMargin=right_margin,
            topMargin=top_margin,
            bottomMargin=bottom_margin
        )
        
        base_styles = getSampleStyleSheet()
        
        # Ultra-compressed styles
        name_style = ParagraphStyle(
            'NameStyle',
            parent=base_styles['Heading1'],
            fontSize=16 if original_page_count == 1 else 18,
            spaceAfter=2,
            spaceBefore=0,
            alignment=TA_CENTER,
            textColor=black,
            fontName='Helvetica-Bold',
            leading=18 if original_page_count == 1 else 20
        )
        
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=base_styles['Normal'],
            fontSize=8 if original_page_count == 1 else 9,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=black,
            fontName='Helvetica',
            leading=9 if original_page_count == 1 else 10
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeaderStyle',
            parent=base_styles['Heading2'],
            fontSize=10 if original_page_count == 1 else 11,
            spaceAfter=3,
            spaceBefore=6,
            fontName='Helvetica-Bold',
            textColor=black,
            alignment=TA_LEFT,
            leading=11 if original_page_count == 1 else 12
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=base_styles['Normal'],
            fontSize=base_font_size,
            spaceAfter=2,
            spaceBefore=0,
            fontName='Helvetica',
            textColor=black,
            alignment=TA_LEFT,
            leading=base_font_size + 2
        )
        
        story = []
        
        # Add compressed content
        if 'name' in sections:
            name = sections['name'].replace('**', '').replace('*', '').strip()
            story.append(Paragraph(name, name_style))
        
        if 'contact' in sections:
            contact = sections['contact'].replace('**', '').replace('*', '').strip()
            contact_lines = [line.strip() for line in contact.split('\n') if line.strip()]
            if contact_lines:
                formatted_contact = ' | '.join(contact_lines)
                story.append(Paragraph(formatted_contact, contact_style))
        
        # Add other sections with minimal spacing
        for section_key in ['summary', 'experience', 'skills', 'education']:
            if section_key in sections and sections[section_key]:
                story.append(Paragraph(section_key.upper(), section_header_style))
                content = sections[section_key].replace('**', '').replace('*', '').strip()
                content_lines = [line.strip() for line in content.split('\n') if line.strip()]
                for line in content_lines:
                    if line and not line.startswith('#'):
                        story.append(Paragraph(line, normal_style))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
        
    except Exception as e:
        print(f"Error creating compressed PDF: {e}")
        return create_fallback_text_pdf(resume_data)


def create_docx_resume(resume_data, visual_description):
    """Create an editable DOCX version of the resume"""
    try:
        # Create new document
        doc = Document()
        
        # Set document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.7)
            section.right_margin = Inches(0.7)
        
        # Parse resume sections
        sections = parse_structured_resume_data(resume_data)
        
        # Add name (title)
        name = sections.get('name', 'Professional Resume')
        clean_name = name.replace('**', '').replace('*', '').strip()
        name_para = doc.add_paragraph()
        name_run = name_para.add_run(clean_name)
        name_run.font.size = Pt(18)
        name_run.font.name = 'Calibri'
        name_run.bold = True
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add contact information
        contact = sections.get('contact', '')
        if contact:
            clean_contact = contact.replace('**', '').replace('*', '').strip()
            contact_lines = [line.strip() for line in clean_contact.split('\n') if line.strip()]
            if contact_lines:
                contact_para = doc.add_paragraph()
                contact_run = contact_para.add_run(' | '.join(contact_lines))
                contact_run.font.size = Pt(11)
                contact_run.font.name = 'Calibri'
                contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add spacing
        doc.add_paragraph()
        
        # Add professional summary
        summary = sections.get('summary', '')
        if summary:
            # Section header
            summary_header = doc.add_paragraph()
            summary_run = summary_header.add_run('PROFESSIONAL SUMMARY')
            summary_run.font.size = Pt(12)
            summary_run.font.name = 'Calibri'
            summary_run.bold = True
            
            # Add horizontal line
            doc.add_paragraph('_' * 80)
            
            clean_summary = summary.replace('**', '').replace('*', '').strip()
            summary_paragraphs = [p.strip() for p in clean_summary.split('\n') if p.strip()]
            for para in summary_paragraphs:
                summary_para = doc.add_paragraph()
                summary_text = summary_para.add_run(para)
                summary_text.font.size = Pt(11)
                summary_text.font.name = 'Calibri'
            
            doc.add_paragraph()
        
        # Add professional experience
        experience = sections.get('experience', '')
        if experience:
            exp_header = doc.add_paragraph()
            exp_run = exp_header.add_run('PROFESSIONAL EXPERIENCE')
            exp_run.font.size = Pt(12)
            exp_run.font.name = 'Calibri'
            exp_run.bold = True
            
            # Add horizontal line
            doc.add_paragraph('_' * 80)
            
            exp_lines = [line.strip() for line in experience.split('\n') if line.strip()]
            
            i = 0
            while i < len(exp_lines):
                line = exp_lines[i].replace('**', '').replace('*', '').strip()
                
                if not line or line.startswith('#'):
                    i += 1
                    continue
                
                # Check if this looks like a job entry
                if ('|' in line and ('20' in line or 'Present' in line)) or \
                   (any(keyword in line.lower() for keyword in ['manager', 'director', 'analyst', 'specialist', 'coordinator', 'assistant', 'associate', 'senior', 'junior', 'lead'])):
                    
                    # Job title and company
                    if '|' in line:
                        parts = [p.strip() for p in line.split('|')]
                        job_title = parts[0].strip()
                        company_date = ' | '.join(parts[1:]).strip()
                        
                        # Job title
                        job_para = doc.add_paragraph()
                        job_run = job_para.add_run(job_title)
                        job_run.font.size = Pt(11)
                        job_run.font.name = 'Calibri'
                        job_run.bold = True
                        
                        # Company and date
                        company_para = doc.add_paragraph()
                        company_run = company_para.add_run(company_date)
                        company_run.font.size = Pt(10)
                        company_run.font.name = 'Calibri'
                        company_run.italic = True
                    else:
                        job_para = doc.add_paragraph()
                        job_run = job_para.add_run(line)
                        job_run.font.size = Pt(11)
                        job_run.font.name = 'Calibri'
                        job_run.bold = True
                    
                    # Add bullets
                    i += 1
                    bullet_count = 0
                    while i < len(exp_lines) and bullet_count < 4:
                        next_line = exp_lines[i].replace('**', '').replace('*', '').strip()
                        
                        if not next_line:
                            i += 1
                            continue
                        
                        if next_line.startswith(('•', '*', '-')) or \
                           (not next_line.startswith(('**', '#')) and len(next_line) > 20 and not ('|' in next_line and ('20' in next_line or 'Present' in next_line))):
                            
                            bullet_text = next_line
                            for prefix in ['•', '*', '-']:
                                if bullet_text.startswith(prefix):
                                    bullet_text = bullet_text[1:].strip()
                                    break
                            
                            if bullet_text:
                                bullet_para = doc.add_paragraph()
                                bullet_para.style = 'List Bullet'
                                bullet_run = bullet_para.add_run(bullet_text)
                                bullet_run.font.size = Pt(10)
                                bullet_run.font.name = 'Calibri'
                                bullet_count += 1
                        
                        elif ('|' in next_line and ('20' in next_line or 'Present' in next_line)) or \
                             (any(keyword in next_line.lower() for keyword in ['manager', 'director', 'analyst', 'specialist', 'coordinator', 'assistant', 'associate', 'senior', 'junior', 'lead'])):
                            break
                        
                        i += 1
                    
                    # Add spacing between jobs
                    doc.add_paragraph()
                    continue
                
                i += 1
            
            doc.add_paragraph()
        
        # Add skills
        skills = sections.get('skills', '')
        if skills:
            skills_header = doc.add_paragraph()
            skills_run = skills_header.add_run('SKILLS')
            skills_run.font.size = Pt(12)
            skills_run.font.name = 'Calibri'
            skills_run.bold = True
            
            # Add horizontal line
            doc.add_paragraph('_' * 80)
            
            skill_lines = [line.strip() for line in skills.split('\n') if line.strip()]
            for line in skill_lines:
                line = line.replace('**', '').replace('*', '').strip()
                if line and not line.startswith('#'):
                    skill_para = doc.add_paragraph()
                    skill_run = skill_para.add_run(line)
                    skill_run.font.size = Pt(10)
                    skill_run.font.name = 'Calibri'
            
            doc.add_paragraph()
        
        # Add education
        education = sections.get('education', '')
        if education:
            edu_header = doc.add_paragraph()
            edu_run = edu_header.add_run('EDUCATION')
            edu_run.font.size = Pt(12)
            edu_run.font.name = 'Calibri'
            edu_run.bold = True
            
            # Add horizontal line
            doc.add_paragraph('_' * 80)
            
            edu_lines = [line.strip() for line in education.split('\n') if line.strip()]
            for line in edu_lines:
                line = line.replace('**', '').replace('*', '').strip()
                if line and not line.startswith('#'):
                    edu_para = doc.add_paragraph()
                    edu_run = edu_para.add_run(line)
                    edu_run.font.size = Pt(10)
                    edu_run.font.name = 'Calibri'
        
        # Save to buffer
        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        
        return docx_buffer
        
    except Exception as e:
        print(f"Error creating DOCX: {e}")
        return None


# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/previews/<filename>')
def serve_preview(filename):
    return send_from_directory(app.config['PREVIEW_FOLDER'], filename)

@app.route('/generate', methods=['POST'])
def generate_resume():
    print("DEBUG: Received request at /generate endpoint")
    if 'resumeFile' not in request.files or 'jobUrl' not in request.form:
        print("ERROR: Missing form data")
        return jsonify({'error': 'Missing form data'}), 400

    resume_file = request.files['resumeFile']
    job_url = request.form['jobUrl']

    print(f"DEBUG: Received job URL: {job_url}")
    print(f"DEBUG: Received resume file: {resume_file.filename}")

    try:
        resume_text, original_page_count = extract_text_from_pdf(resume_file)
        print(f"DEBUG: Extracted text from PDF with {original_page_count} pages")
    except Exception as e:
        print(f"ERROR: Failed to extract text from PDF: {e}")
        return jsonify({'error': 'Could not extract text from the uploaded PDF.'}), 500

    job_description = scrape_job_description(job_url)
    if not job_description:
        print("ERROR: Failed to scrape job description")
        return jsonify({'error': 'Could not scrape job description from the URL.'}), 500

    print("DEBUG: Scraped job description")
    ai_response = get_gemini_response(job_description, resume_text, original_page_count)
    print(f"DEBUG: AI response: {ai_response}")

    if not ai_response or ai_response == "AI generation failed." or ai_response == "Error: AI returned an empty response.":
        print("ERROR: Invalid or empty response from Gemini")
        return jsonify({'error': 'Failed to generate resume content.'}), 500

    # Parse AI response to get resume data, visual description, and explanation
    resume_data, visual_description, transformation_explanation = parse_ai_response(ai_response)
    print(f"DEBUG: Resume data length: {len(resume_data)}")
    print(f"DEBUG: First 300 chars of resume data: {resume_data[:300]}")
    print(f"DEBUG: Transformation explanation: {transformation_explanation[:200]}...")

    # CRITICAL: Validate for placeholder text that would require user editing
    placeholder_errors, weak_language = validate_resume_content(resume_data)
    if placeholder_errors:
        print(f"ERROR: Resume contains placeholder text: {placeholder_errors}")
        error_msg = f"Resume generation failed - contains incomplete sections that would require manual editing. This is not allowed. Found: {', '.join(placeholder_errors[:3])}"
        return jsonify({'error': error_msg}), 500
    
    # Log weak language for aggressive transformation feedback
    if weak_language:
        print(f"WARNING: Resume contains weak language that should be transformed: {weak_language[:5]}")
        # Continue processing but note for improvement

    # Check if AI is asking for job description
    if ("Please provide the job description" in resume_data or "job description" in resume_data.lower()) and len(resume_data) < 500:
        print("DEBUG: AI requesting job description, will proceed with general optimization")
        # Re-prompt with emphasis on general enhancement
        enhanced_prompt = f"""
        You are an expert resume writer. Create an enhanced, professional version of this resume.
        
        REQUIREMENTS:
        - Enhance the original resume content to make it more impactful and professional
        - Strengthen the summary with compelling language
        - Improve experience bullets with action verbs and quantified achievements
        - Organize skills effectively
        - Maintain the original structure and information
        - Output complete resume content ready for formatting
        
        ORIGINAL RESUME:
        {resume_text}
        
        OUTPUT FORMAT:
        Name: [Original name]
        Contact: [Original contact information]
        Summary: [Enhanced professional summary]
        Experience: [Enhanced experience section with improved bullets]
        Skills: [Organized skills section]
        Education: [Original education information]
        """
        
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            enhanced_response = model.generate_content(enhanced_prompt)
            if enhanced_response and enhanced_response.text:
                resume_data = enhanced_response.text
                visual_description = "Professional resume format with clear sections and consistent styling"
                transformation_explanation = """
                • Resume content enhanced with professional language and improved structure
                • Experience bullets strengthened with action verbs and quantified achievements
                • Skills section reorganized for maximum impact and relevance
                • Overall presentation upgraded to meet current professional standards
                """
                print(f"DEBUG: Enhanced resume data length: {len(resume_data)}")
            else:
                print("ERROR: Failed to get enhanced resume content")
                return jsonify({'error': 'Failed to enhance resume content.'}), 500
        except Exception as e:
            print(f"ERROR: Failed to generate enhanced resume: {e}")
            return jsonify({'error': 'Failed to enhance resume content.'}), 500

    # Validate that we got substantial resume data
    if len(resume_data.strip()) < 100:  # Reduced threshold but still ensure we have content
        print("ERROR: Generated resume data too short to be complete")
        return jsonify({'error': 'Generated resume appears incomplete.'}), 500

    try:
        file_buffer = create_ai_formatted_pdf(resume_data, visual_description, original_page_count)
        print(f"DEBUG: Created professional text-based PDF limited to {original_page_count} page(s)")
        
        # Verify the PDF was actually created with content
        if file_buffer.getbuffer().nbytes < 1000:  # A proper PDF should be at least 1KB
            print("ERROR: Generated PDF is suspiciously small")
            return jsonify({'error': 'Generated PDF appears invalid.'}), 500
    except Exception as e:
        print(f"ERROR: Failed to create PDF: {e}")
        return jsonify({'error': 'Could not create PDF.'}), 500

    # Create DOCX version
    try:
        docx_buffer = create_docx_resume(resume_data, visual_description)
        print("DEBUG: Created editable DOCX version")
        
        if not docx_buffer or docx_buffer.getbuffer().nbytes < 1000:
            print("WARNING: DOCX creation failed or file too small")
            docx_buffer = None
    except Exception as e:
        print(f"WARNING: Failed to create DOCX: {e}")
        docx_buffer = None

    unique_id = uuid.uuid4().hex
    
    # Save PDF
    pdf_filename = f"{unique_id}_resume.pdf"
    pdf_filepath = os.path.join(app.config['PREVIEW_FOLDER'], pdf_filename)
    try:
        with open(pdf_filepath, 'wb') as f:
            f.write(file_buffer.getbuffer())
        print(f"DEBUG: Saved PDF to {pdf_filepath}")
    except Exception as e:
        print(f"ERROR: Failed to save PDF: {e}")
        return jsonify({'error': 'Could not save PDF.'}), 500

    # Save DOCX if created successfully
    docx_url = None
    if docx_buffer:
        docx_filename = f"{unique_id}_resume.docx"
        docx_filepath = os.path.join(app.config['PREVIEW_FOLDER'], docx_filename)
        try:
            with open(docx_filepath, 'wb') as f:
                f.write(docx_buffer.getbuffer())
            docx_url = f"/previews/{docx_filename}"
            print(f"DEBUG: Saved DOCX to {docx_filepath}")
        except Exception as e:
            print(f"WARNING: Failed to save DOCX: {e}")

    pdf_url = f"/previews/{pdf_filename}"
    print(f"DEBUG: Returning PDF URL: {pdf_url}")
    if docx_url:
        print(f"DEBUG: Returning DOCX URL: {docx_url}")
    
    response_data = {'preview_url': pdf_url, 'explanation': transformation_explanation}
    if docx_url:
        response_data['docx_url'] = docx_url
        
    return jsonify(response_data)

if __name__ == '__main__':
    # Allow access from all network interfaces (including mobile devices)
    app.run(debug=True, host='0.0.0.0', port=8080)
