
# Resume Generator - AI-Powered Resume Enhancement

## Project Overview
This is an AI-powered resume generator that transforms resumes to match specific job descriptions using Google's Gemini AI. The system provides detailed explanations of all transformations made.

## Features
- **AI-Powered Transformations**: Aggressively transforms resumes to match job descriptions
- **Explanation Boxes**: Shows detailed explanations of what changes were made and why
- **Multiple Formats**: Supports PDF and DOCX output
- **Name Parsing**: Robust name detection from various resume formats
- **Job Description Scraping**: Can extract job descriptions from URLs
- **Professional Formatting**: Creates clean, corporate-ready resumes

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Running the Application
```bash
# Start the Flask app
./venv/bin/python app.py

# In another terminal, start ngrok for public access
ngrok http 8080
```

## Project Structure
```
resume-gen/
├── app.py                     # Main Flask application
├── templates/
│   └── index.html            # Frontend interface with explanation boxes
├── static/
│   ├── style.css            # Styling including explanation box design
│   └── script.js            # JavaScript for explanation display
├── previews/                # Generated resume previews
├── test_*.py               # Various test files
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
└── README.md             # This file
```

## Key Components

### Backend (app.py)
- **AI Integration**: Uses Google Gemini for resume transformation
- **Three-Section Response**: TRANSFORMATION_EXPLANATION, VISUAL_RESUME_IMAGE_DESCRIPTION, TAILORED_RESUME_DATA
- **Name Parsing**: Enhanced detection for various resume formats
- **PDF Generation**: Professional formatting with page count constraints

### Frontend
- **Explanation Boxes**: Display transformation details above resume preview
- **Responsive Design**: Works on desktop and mobile
- **File Upload**: Supports PDF resume uploads
- **Job Description Input**: Text area or URL input

### Styling
- **Professional Design**: Corporate-appropriate colors and fonts
- **Explanation Boxes**: Blue-purple gradient with clear typography
- **Mobile Responsive**: Optimized for all screen sizes

## Usage

1. **Upload Resume**: Select a PDF file of the original resume
2. **Add Job Description**: Either paste text or provide a URL
3. **Generate**: Click "Generate Resume" button
4. **Review Explanation**: Read the detailed transformation explanation above the preview
5. **Download**: Get your enhanced resume in PDF or DOCX format

## API Endpoints

### POST /generate
Generates an enhanced resume based on job description and original resume.

**Parameters:**
- `resume_file`: PDF file of original resume
- `job_description`: Job description text or URL
- `format`: Output format ("pdf" or "docx")

**Response:** 
- Enhanced resume file with transformation explanations

## Testing
Run the test files to verify functionality:
```bash
./venv/bin/python test_explanation_feature.py
./venv/bin/python test_name_parsing.py
./venv/bin/python test_complete_generation.py
```

## Troubleshooting

### Common Issues
1. **Port 8080 in use**: Run `lsof -ti:8080 | xargs kill -9`
2. **Ngrok offline**: Restart with `ngrok http 8080`
3. **Missing API key**: Check `.env` file has `GOOGLE_API_KEY`

### Dependencies
If you get import errors, reinstall dependencies:
```bash
pip install flask google-generativeai python-dotenv requests beautifulsoup4 pdfplumber pillow reportlab python-docx
```

## Development Notes

### Recent Enhancements
- Added explanation feature with detailed transformation descriptions
- Enhanced name parsing to handle multiple resume formats
- Improved AI prompting for aggressive job-specific transformations
- Added mobile-responsive design
- Implemented three-section AI response parsing

### Code Architecture
- Modular design with separate functions for parsing, generation, and formatting
- Robust error handling and fallback mechanisms
- Professional PDF generation with page count constraints
- Clean separation between backend AI logic and frontend presentation

## Future Enhancements
- Database storage for generated resumes
- User accounts and resume history
- Additional output formats (HTML, plain text)
- Batch processing for multiple resumes
- Integration with job boards for automatic application

## Support
For issues or questions, check the test files for examples of proper usage and troubleshooting steps.

## The Problem

Manually editing a resume for each job application is time-consuming and often ineffective. Job seekers need a way to quickly and intelligently tailor their resume to match the specific requirements of a job description, increasing their chances of getting noticed by recruiters and passing through Applicant Tracking Systems (ATS).

## The Solution

`resume-gen` is a web application that automates the resume tailoring process. It uses AI to analyze a job description and rewrite a user's resume to highlight the most relevant skills and experiences. The application then reconstructs the resume, preserving the original formatting, and provides a downloadable PDF.

### How It Works

1.  **Upload and Scrape:** The user uploads their existing resume as a PDF and provides a URL to a job posting. The application extracts the structured content from the resume and scrapes the job description from the provided URL.
2.  **AI-Powered Rewrite:** The extracted resume text and job description are sent to a generative AI model (Google's Gemini). The model rewrites the resume content, focusing on the summary and experience sections, to align with the job requirements.
3.  **Reconstruct and Preview:** The application rebuilds the resume in PDF format, carefully reapplying the original fonts, sizes, and layout. A preview of the tailored resume is then displayed to the user.
4.  **Download:** The user can download the newly generated, tailored resume as a PDF.

## Key Features

*   **AI-Powered Content Generation:** Leverages Google's Gemini model to create highly relevant and effective resume content.
*   **Style Preservation:** Reconstructs the resume to maintain the original visual style, including fonts, text sizes, and layout.
*   **Web-Based Interface:** An easy-to-use web interface for uploading resumes and previewing the results.
*   **PDF Support:** Works with PDF resumes, one of the most common formats for job applications.

## Getting Started

### Prerequisites

*   Python 3.7+
*   Flask
*   Google Generative AI SDK (`google-generativeai`)
*   PyMuPDF (`fitz`)
*   FPDF (`fpdf`)
*   python-dotenv
*   requests
*   BeautifulSoup4

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd resume-gen
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install Flask google-generativeai PyMuPDF fpdf python-dotenv requests beautifulsoup4
    ```

4.  **Set up your environment variables:**
    Create a `.env` file in the root of the project and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY"
    ```

### Running the Application

1.  **Start the Flask server:**
    ```bash
    python app.py
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:8080` to use the application.
