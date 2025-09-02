"""
Clean Flask Resume Generator App with Ad Monetization
"""

from flask import Flask, request, render_template, jsonify, send_file
import os
import logging
import uuid
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
PREVIEWS_FOLDER = 'previews'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PREVIEWS_FOLDER, exist_ok=True)

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

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    """Generate resume with AI enhancement"""
    try:
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        output_format = request.form.get('format', 'pdf')
        
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
        enhanced_resume_path = process_resume_with_ai(filepath, job_description, output_format)
        
        # Update analytics
        analytics_data['total_resumes_generated'] += 1
        
        # Return success
        return jsonify({
            'success': True,
            'preview_url': f'/preview/{os.path.basename(enhanced_resume_path)}',
            'download_url': f'/download/{os.path.basename(enhanced_resume_path)}'
        })
        
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500

def process_resume_with_ai(resume_path: str, job_description: str, output_format: str) -> str:
    """Process resume with AI enhancement - placeholder for now"""
    output_filename = f"{uuid.uuid4()}_enhanced_resume.{output_format}"
    output_path = os.path.join(PREVIEWS_FOLDER, output_filename)
    
    # For now, just copy the original file
    # TODO: Implement actual AI processing here
    shutil.copy2(resume_path, output_path)
    
    return output_path

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
