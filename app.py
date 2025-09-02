"""
Enhanced Flask app with ad monetization and analytics integration
"""

from flask import Flask, request, render_template, jsonify, send_file
import os
import logging
import uuid
import io
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
PREVIEWS_FOLDER = 'previews'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PREVIEWS_FOLDER, exist_ok=True)

# Analytics data store (in production, use a database)
analytics_data = {
    'daily_users': 0,
    'total_resumes_generated': 0,
    'popular_industries': {},
    'user_data': []
}

def track_user_analytics(user_data: dict):
    """Track user behavior for ad targeting and monetization"""
    analytics_data['user_data'].append({
        'timestamp': datetime.now().isoformat(),
        'session_id': user_data.get('session_id'),
        'industry': user_data.get('industry'),
        'experience_level': user_data.get('experience_level'),
        'job_keywords': user_data.get('job_keywords', []),
        'location_hint': user_data.get('location_hint'),
        'company_size_preference': user_data.get('company_size_preference')
    })
    
    # Update industry tracking for ad targeting
    industry = user_data.get('industry', 'general')
    analytics_data['popular_industries'][industry] = analytics_data['popular_industries'].get(industry, 0) + 1
    
    logger.info(f"Analytics tracked: {user_data.get('industry')} industry user")

def extract_job_insights(job_description: str) -> dict:
    """Extract valuable insights from job description for analytics"""
    insights = {
        'industry': 'general',
        'experience_level': 'mid_level',
        'company_size': 'unknown',
        'location_hints': [],
        'tech_stack': [],
        'salary_indicators': []
    }
    
    text_lower = job_description.lower()
    
    # Industry detection
    industry_keywords = {
        'technology': ['software', 'developer', 'engineer', 'tech', 'programming', 'coding'],
        'healthcare': ['healthcare', 'medical', 'hospital', 'nurse', 'doctor', 'clinical'],
        'finance': ['finance', 'banking', 'investment', 'financial', 'accounting'],
        'education': ['education', 'teacher', 'academic', 'university', 'school'],
        'retail': ['retail', 'sales', 'customer service', 'store', 'commerce'],
        'marketing': ['marketing', 'advertising', 'brand', 'digital marketing', 'social media']
    }
    
    for industry, keywords in industry_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            insights['industry'] = industry
            break
    
    # Experience level detection
    if any(term in text_lower for term in ['entry level', 'junior', 'new grad', '0-2 years']):
        insights['experience_level'] = 'entry'
    elif any(term in text_lower for term in ['senior', 'lead', 'principal', '5+ years']):
        insights['experience_level'] = 'senior'
    elif any(term in text_lower for term in ['manager', 'director', 'vp', 'head of']):
        insights['experience_level'] = 'management'
    
    # Tech stack extraction
    tech_keywords = ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker', 'kubernetes']
    insights['tech_stack'] = [tech for tech in tech_keywords if tech in text_lower]
    
    # Company size hints
    if any(term in text_lower for term in ['startup', 'small team', 'growing company']):
        insights['company_size'] = 'startup'
    elif any(term in text_lower for term in ['enterprise', 'fortune 500', 'large corporation']):
        insights['company_size'] = 'enterprise'
    
    return insights

@app.route('/')
def index():
    """Serve the main page with ad integration"""
    session_id = str(uuid.uuid4())
    
    # Track page view
    analytics_data['daily_users'] += 1
    
    # Use clean template with working AdSense
    return render_template('index.html', session_id=session_id)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'app': 'resume-gen'
    })

@app.route('/ads.txt')
def ads_txt():
    """Serve ads.txt file for AdSense verification"""
    try:
        file_path = os.path.join('static', 'ads.txt')
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='text/plain')
        else:
            return "google.com, pub-7524647518323966, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        logger.error(f"Error serving ads.txt: {str(e)}")
        return "google.com, pub-7524647518323966, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    """Generate resume with enhanced analytics tracking"""
    try:
        # Get session ID for tracking
        session_id = request.form.get('session_id', str(uuid.uuid4()))
        
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        output_format = request.form.get('format', 'pdf')
        
        # Extract job insights for analytics
        job_insights = extract_job_insights(job_description)
        
        # Track user data for ad targeting
        user_analytics = {
            'session_id': session_id,
            'industry': job_insights['industry'],
            'experience_level': job_insights['experience_level'],
            'job_keywords': job_insights['tech_stack'][:5],  # Top 5 for privacy
            'company_size_preference': job_insights['company_size'],
            'location_hint': 'extracted_from_job' if job_insights['location_hints'] else None
        }
        track_user_analytics(user_analytics)
        
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
        
        # Process the resume (your existing logic here)
        enhanced_resume_path = process_resume_with_ai(filepath, job_description, output_format)
        
        # Update analytics
        analytics_data['total_resumes_generated'] += 1
        
        # Return success with enhanced analytics data
        return jsonify({
            'success': True,
            'preview_url': f'/preview/{os.path.basename(enhanced_resume_path)}',
            'download_url': f'/download/{os.path.basename(enhanced_resume_path)}',
            'user_insights': {
                'industry_detected': job_insights['industry'],
                'experience_level': job_insights['experience_level'],
                'tech_stack_found': len(job_insights['tech_stack']) > 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500

def process_resume_with_ai(resume_path: str, job_description: str, output_format: str) -> str:
    """Process resume with AI enhancement (your existing logic)"""
    # This would contain your existing resume processing logic
    # For now, returning a placeholder
    output_filename = f"{uuid.uuid4()}_enhanced_resume.{output_format}"
    output_path = os.path.join(PREVIEWS_FOLDER, output_filename)
    
    # Your AI processing logic here...
    # For demo purposes, just copy the original file
    import shutil
    shutil.copy2(resume_path, output_path)
    
    return output_path

@app.route('/analytics-data')
def get_analytics_data():
    """Get analytics data for ad optimization"""
    summary = {
        'total_users_today': analytics_data['daily_users'],
        'total_resumes_generated': analytics_data['total_resumes_generated'],
        'top_industries': dict(sorted(analytics_data['popular_industries'].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]),
        'user_segments': {
            'entry_level': len([u for u in analytics_data['user_data'] 
                              if u.get('experience_level') == 'entry']),
            'mid_level': len([u for u in analytics_data['user_data'] 
                            if u.get('experience_level') == 'mid_level']),
            'senior_level': len([u for u in analytics_data['user_data'] 
                               if u.get('experience_level') == 'senior']),
            'management': len([u for u in analytics_data['user_data'] 
                             if u.get('experience_level') == 'management'])
        }
    }
    return jsonify(summary)

@app.route('/ad-targeting-data')
def get_ad_targeting_data():
    """Get data for ad network targeting (anonymized)"""
    recent_users = analytics_data['user_data'][-100:]  # Last 100 users
    
    targeting_data = {
        'audience_segments': {
            'job_seekers_tech': len([u for u in recent_users if u.get('industry') == 'technology']),
            'job_seekers_healthcare': len([u for u in recent_users if u.get('industry') == 'healthcare']),
            'job_seekers_finance': len([u for u in recent_users if u.get('industry') == 'finance']),
            'career_changers': len([u for u in recent_users if len(u.get('job_keywords', [])) > 3]),
            'entry_level_professionals': len([u for u in recent_users 
                                            if u.get('experience_level') == 'entry'])
        },
        'high_intent_indicators': {
            'multiple_resumes_generated': analytics_data['total_resumes_generated'] > 1000,
            'diverse_industries': len(analytics_data['popular_industries']) > 3,
            'active_job_market': analytics_data['daily_users'] > 50
        }
    }
    
    return jsonify(targeting_data)

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
    """Serve download files with tracking"""
    try:
        file_path = os.path.join(PREVIEWS_FOLDER, filename)
        if os.path.exists(file_path):
            # Track download for analytics
            analytics_data['total_resumes_generated'] += 1
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        logger.error(f"Error serving download: {str(e)}")
        return "Error serving file", 500

@app.route('/privacy')
def privacy_policy():
    """Privacy policy page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Privacy Policy - AI Resume Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1, h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Privacy Policy</h1>
        <h2>Data Collection</h2>
        <p>We collect anonymized data about job market trends, industry preferences, and user behavior to improve our service and provide relevant career-related advertisements.</p>
        
        <h2>Data Usage</h2>
        <p>Your data helps us:</p>
        <ul>
            <li>Improve AI resume generation quality</li>
            <li>Show relevant career services and job opportunities</li>
            <li>Provide industry insights and trends</li>
        </ul>
        
        <h2>Data Sharing</h2>
        <p>We may share anonymized, aggregated data with career service partners and advertisers to provide relevant opportunities.</p>
        
        <h2>Your Rights</h2>
        <p>You can request data deletion or modification by contacting us.</p>
        
        <p><a href="/">Back to Resume Generator</a></p>
    </body>
    </html>
    """

@app.route('/terms')
def terms_of_service():
    """Terms of service page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terms of Service - AI Resume Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1, h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Terms of Service</h1>
        <h2>Service Description</h2>
        <p>AI Resume Generator provides AI-powered resume enhancement services free of charge, supported by advertising.</p>
        
        <h2>User Responsibilities</h2>
        <ul>
            <li>Provide accurate information in your resume</li>
            <li>Use the service for legitimate job seeking purposes</li>
            <li>Respect intellectual property rights</li>
        </ul>
        
        <h2>Service Limitations</h2>
        <p>We provide AI-generated suggestions. Users are responsible for verifying accuracy and appropriateness.</p>
        
        <h2>Advertising</h2>
        <p>Our free service is supported by relevant career-related advertisements and partnerships.</p>
        
        <p><a href="/">Back to Resume Generator</a></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
