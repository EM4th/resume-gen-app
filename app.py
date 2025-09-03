"""
Clean Flask Resume Generator App with Ad Monetization
"""

from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
import os
import logging
import uuid
from datetime import datetime
import shutil
import google.generativeai as genai
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
PREVIEWS_FOLDER = 'previews'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PREVIEWS_FOLDER, exist_ok=True)

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    logger.warning("GOOGLE_API_KEY not found. AI features will be disabled.")

# Simple analytics tracking
analytics_data = {
    'daily_users': 0,
    'total_resumes_generated': 0
}

@app.route('/')
def index():
    """Serve the main page with ad integration"""
    analytics_data['daily_users'] += 1
    session_id = str(uuid.uuid4())
    return render_template('index.html', session_id=session_id)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0',
        'app': 'resume-gen'
    })

@app.route('/ads.txt')
def ads_txt():
    """Serve ads.txt file for AdSense verification"""
    try:
        # Try to serve from root directory first
        file_path = 'ads.txt'
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='text/plain')
        # Fallback content
        return "google.com, pub-7524647518323966, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        logger.error(f"Error serving ads.txt: {str(e)}")
        return "google.com, pub-7524647518323966, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

@app.route('/test')
def test():
    return render_template('test_simple.html')

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    """Generate resume with AI enhancement"""
    try:
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        output_format = request.form.get('format', 'pdf')
        
        # Validate input
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Check if resume file was uploaded
        if 'resume_file' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save uploaded file
        filename = f"{uuid.uuid4()}_resume.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process the resume
        enhanced_resume_path, explanation = process_resume_with_ai(filepath, job_description, output_format)
        
        # Update analytics
        analytics_data['total_resumes_generated'] += 1
        
        # Return success with explanation
        return jsonify({
            'success': True,
            'preview_url': f'/preview/{os.path.basename(enhanced_resume_path)}',
            'download_url': f'/download/{os.path.basename(enhanced_resume_path)}',
            'explanation': explanation
        })
        
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500

def process_resume_with_ai(resume_path: str, job_description: str, output_format: str) -> tuple[str, str]:
    """Process resume with AI enhancement and return file path and explanation"""
    try:
        # Extract text from uploaded resume
        resume_text = extract_text_from_pdf(resume_path)
        
        if not resume_text.strip():
            raise ValueError("Could not extract text from PDF")
        
        # Generate enhanced resume with AI
        if model:
            enhanced_content, explanation = enhance_resume_with_ai(resume_text, job_description)
        else:
            # Fallback: basic processing without AI
            enhanced_content = resume_text
            explanation = "AI enhancement unavailable. Original resume returned."
            logger.warning("AI processing disabled, returning original content")
        
        # Generate output file
        output_filename = f"{uuid.uuid4()}_enhanced_resume.{output_format}"
        output_path = os.path.join(PREVIEWS_FOLDER, output_filename)
        
        if output_format.lower() == 'pdf':
            create_pdf_resume(enhanced_content, output_path)
        else:
            # For now, just copy the original for non-PDF formats
            shutil.copy2(resume_path, output_path)
        
        return output_path, explanation
        
    except Exception as e:
        logger.error(f"Error in AI processing: {str(e)}")
        # Fallback: just copy the original file
        output_filename = f"{uuid.uuid4()}_resume.{output_format}"
        output_path = os.path.join(PREVIEWS_FOLDER, output_filename)
        shutil.copy2(resume_path, output_path)
        return output_path, "Error occurred during AI enhancement. Original resume returned."

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def enhance_resume_with_ai(resume_text: str, job_description: str) -> tuple[str, str]:
    """Use AI to enhance resume based on job description and return both enhanced content and explanation"""
    try:
        # First, get the enhanced resume with better formatting instructions
        enhance_prompt = f"""
        You are an expert resume writer and career coach. Please enhance the following resume to better match the job description while maintaining professional formatting.

        ORIGINAL RESUME:
        {resume_text}

        JOB DESCRIPTION:
        {job_description}

        Please provide an enhanced version that:
        1. Maintains all original factual information (names, dates, companies, etc.)
        2. Improves wording using stronger action verbs and industry keywords
        3. Better highlights relevant skills and experiences for this specific job
        4. Quantifies achievements where possible with numbers/percentages
        5. Uses proper resume formatting with clear sections
        6. Maintains professional tone and structure

        IMPORTANT FORMATTING REQUIREMENTS:
        - Keep the candidate's name at the top
        - Organize content in clear sections (Contact, Summary/Objective, Experience, Education, Skills, etc.)
        - Use bullet points for job responsibilities and achievements
        - Maintain consistent formatting throughout
        - Ensure each section is clearly separated

        Return only the enhanced resume text with proper formatting:
        """
        
        enhanced_response = model.generate_content(enhance_prompt)
        enhanced_content = enhanced_response.text
        
        # Now get a detailed explanation of changes
        explanation_prompt = f"""
        You are an expert resume writer. I have enhanced a resume for this specific job description. Please provide a clear, engaging explanation of the key improvements made to help this candidate succeed.

        JOB THEY'RE APPLYING FOR:
        {job_description}

        Please provide a concise explanation (3-5 bullet points) of the most impactful improvements made to better match this job and why they increase the candidate's chances.

        Focus on specific improvements like:
        - Relevant keywords and skills highlighted that match the job requirements
        - Professional language and stronger action verbs used
        - Technical skills and experiences emphasized for this role
        - Achievements better presented or quantified
        - Overall presentation improved for this specific position

        Format as engaging bullet points:
        • Enhanced [specific area]: [brief explanation of why this helps for this job]
        • Improved [specific area]: [brief explanation of value added]
        • Added [specific improvement]: [why this matters for this role]

        Keep it professional but engaging, showing clear value for this specific job opportunity:
        """
        
        explanation_response = model.generate_content(explanation_prompt)
        explanation = explanation_response.text
        
        return enhanced_content, explanation
        
    except Exception as e:
        logger.error(f"Error in AI enhancement: {str(e)}")
        return resume_text, f"AI enhancement temporarily unavailable. Please try again. Error: {str(e)}"

def create_pdf_resume(content: str, output_path: str):
    """Create a professionally formatted PDF from resume content"""
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Define custom styles for better resume formatting
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        
        # Custom styles for resume sections
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.black,
            borderWidth=1,
            borderColor=colors.black,
            borderPadding=4
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceBefore=4,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leftIndent=20
        )
        
        # Process content line by line for better formatting
        lines = content.split('\n')
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line - end current paragraph
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    
                    # Determine style based on content
                    if len(para_text) < 60 and not any(word in para_text.lower() for word in ['experience', 'education', 'skills', 'summary', 'objective']):
                        # Likely a name/title
                        p = Paragraph(para_text, title_style)
                    elif any(word in para_text.lower() for word in ['experience', 'education', 'skills', 'summary', 'objective', 'contact', 'certifications']):
                        # Section header
                        p = Paragraph(para_text.upper(), section_style)
                    else:
                        # Regular content
                        p = Paragraph(para_text, body_style)
                    
                    story.append(p)
                    current_paragraph = []
                    story.append(Spacer(1, 6))
            else:
                current_paragraph.append(line)
        
        # Add any remaining content
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            p = Paragraph(para_text, body_style)
            story.append(p)
        
        doc.build(story)
        
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        # If PDF creation fails, create a simple fallback
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph(content, styles['Normal'])]
            doc.build(story)
        except:
            # Last resort - just copy the original
            raise e

@app.route('/preview/<filename>')
def preview_file(filename):
    """Serve preview files"""
    try:
        file_path = os.path.join(PREVIEWS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=False)
        else:
            return "File not found", 404
    except Exception as e:
        logger.error(f"Error serving preview: {str(e)}")
        return "Error serving file", 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve download files"""
    try:
        file_path = os.path.join(PREVIEWS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        logger.error(f"Error serving download: {str(e)}")
        return "Error serving file", 500

@app.route('/analytics')
def get_analytics():
    """Get basic analytics data"""
    return jsonify({
        'daily_users': analytics_data['daily_users'],
        'total_resumes_generated': analytics_data['total_resumes_generated']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
