document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resumeForm');
    const loadingDiv = document.getElementById('loadingIndicator');
    const successDiv = document.getElementById('successContainer');
    const uploadSection = document.getElementById('uploadSection');
    const submitBtn = document.getElementById('generateBtn');

    if (!form) {
        console.error('Form not found');
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const jobDescription = document.getElementById('jobDescription').value;
        const resumeFile = document.getElementById('resume').files[0];
        const format = document.getElementById('format').value;

        // Validation
        if (!resumeFile) {
            alert('Please select a resume file.');
            return;
        }

        if (!jobDescription.trim()) {
            alert('Please enter a job description.');
            return;
        }

        // Show loading state
        uploadSection.style.display = 'none';
        successDiv.style.display = 'none';
        loadingDiv.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating...';
        
        console.log('Loading state set - upload hidden, loading shown');

        try {
            const formData = new FormData();
            formData.append('job_description', jobDescription);
            formData.append('resume_file', resumeFile);
            formData.append('format', format);

            const response = await fetch('/generate_resume', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            console.log('Backend response:', data);

            if (!response.ok) {
                throw new Error(data.error || 'Server error occurred');
            }

            if (!data.success || !data.preview_url) {
                throw new Error('Server response missing required data');
            }

            console.log('Success! Showing success container...');
            console.log('Data received:', data);
            
            // Force hide everything else first
            uploadSection.style.display = 'none';
            loadingDiv.style.display = 'none';
            
            // Instead of trying to add a download link, let's replace the entire success container content
            successDiv.innerHTML = `
                <div style="text-align: center; padding: 30px; background: white; border: 3px solid green;">
                    <h2 style="color: #667eea; margin-bottom: 20px;">🎉 Your Resume is Ready!</h2>
                    <p style="margin-bottom: 30px; color: #666;">Your AI-enhanced resume has been generated successfully!</p>
                    
                    <a href="${data.download_url || data.preview_url}" 
                       download="enhanced_resume.pdf"
                       style="
                           display: inline-block;
                           padding: 20px 40px;
                           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           color: white;
                           text-decoration: none;
                           border-radius: 12px;
                           font-weight: bold;
                           font-size: 18px;
                           margin: 20px;
                           border: 3px solid #333;
                           box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                           transition: all 0.3s ease;
                       "
                       onmouseover="this.style.transform='translateY(-3px)'"
                       onmouseout="this.style.transform='translateY(0)'"
                    >
                        📥 Download Your Enhanced Resume
                    </a>
                    
                    <div style="margin-top: 30px;">
                        <button onclick="createNewResume()" 
                                style="padding: 12px 24px; margin: 10px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">
                            📄 Create Another Resume
                        </button>
                    </div>
                </div>
            `;
            
            // Force show success with nuclear option CSS
            successDiv.style.cssText = `
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                position: relative !important;
                z-index: 9999 !important;
                margin: 20px 0 !important;
            `;
            
            console.log('Success container completely replaced with new HTML');
            console.log('Download URL:', data.download_url || data.preview_url);

        } catch (error) {
            console.error('Error:', error);
            
            // Hide loading
            loadingDiv.style.display = 'none';
            uploadSection.style.display = 'block';
            
            // Show error
            alert(`Error: ${error.message}`);
            
        } finally {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.textContent = '🎯 Generate Enhanced Resume';
        }
    });

    function addDownloadLink(downloadUrl) {
        console.log('=== addDownloadLink DEBUG START ===');
        console.log('addDownloadLink called with URL:', downloadUrl);
        console.log('successDiv element:', successDiv);
        console.log('successDiv innerHTML before:', successDiv.innerHTML);
        
        // Remove any existing download links
        const existingLinks = successDiv.querySelectorAll('.download-link');
        console.log('Found existing download links:', existingLinks.length);
        existingLinks.forEach(link => link.remove());
        
        // Create download link with VERY obvious styling
        const downloadLink = document.createElement('a');
        downloadLink.href = downloadUrl;
        downloadLink.download = 'enhanced_resume.pdf';
        downloadLink.className = 'action-btn download-link';
        downloadLink.style.cssText = `
            display: block !important;
            margin: 20px auto !important;
            padding: 20px 40px !important;
            background: red !important;
            color: white !important;
            text-decoration: none !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            font-size: 18px !important;
            text-align: center !important;
            border: 3px solid blue !important;
            cursor: pointer !important;
            width: 300px !important;
        `;
        downloadLink.textContent = '📥 DOWNLOAD YOUR RESUME (TEST)';
        
        console.log('Created download link element:', downloadLink);
        console.log('Download link styles:', downloadLink.style.cssText);
        
        // Try multiple ways to add the link
        console.log('Attempting to find .success-message...');
        const successMessage = successDiv.querySelector('.success-message');
        console.log('Found success message:', successMessage);
        
        if (successMessage) {
            console.log('Inserting after success message...');
            successMessage.insertAdjacentElement('afterend', downloadLink);
            console.log('Inserted after success message');
        } else {
            console.log('Success message not found, appending to success div...');
            successDiv.appendChild(downloadLink);
            console.log('Appended to success div');
        }
        
        console.log('successDiv innerHTML after:', successDiv.innerHTML);
        console.log('Download link offsetWidth:', downloadLink.offsetWidth);
        console.log('Download link offsetHeight:', downloadLink.offsetHeight);
        console.log('Download link getBoundingClientRect:', downloadLink.getBoundingClientRect());
        console.log('=== addDownloadLink DEBUG END ===');
    }
});

// Function for "Create New Resume" button
function createNewResume() {
    // Reset form
    document.getElementById('resumeForm').reset();
    
    // Show upload section, hide success
    document.getElementById('uploadSection').style.display = 'block';
    document.getElementById('successContainer').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'none';
    
    // Remove download links
    const existingLinks = document.querySelectorAll('.download-link');
    existingLinks.forEach(link => link.remove());
}
