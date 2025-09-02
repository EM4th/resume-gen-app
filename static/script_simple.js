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

            // Show success
            loadingDiv.style.display = 'none';
            successDiv.style.display = 'block';
            
            // Add download link to success container
            addDownloadLink(data.download_url || data.preview_url);

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
        // Remove any existing download links
        const existingLinks = successDiv.querySelectorAll('.download-link');
        existingLinks.forEach(link => link.remove());
        
        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.href = downloadUrl;
        downloadLink.download = 'enhanced_resume.pdf';
        downloadLink.className = 'action-btn download-link';
        downloadLink.style.cssText = `
            display: inline-block;
            margin: 20px auto;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            text-align: center;
            transition: transform 0.2s;
        `;
        downloadLink.textContent = '📥 Download Your Enhanced Resume';
        
        // Add hover effect
        downloadLink.addEventListener('mouseenter', () => {
            downloadLink.style.transform = 'translateY(-2px)';
        });
        downloadLink.addEventListener('mouseleave', () => {
            downloadLink.style.transform = 'translateY(0)';
        });
        
        // Insert after success message
        const successMessage = successDiv.querySelector('.success-message');
        if (successMessage) {
            successMessage.insertAdjacentElement('afterend', downloadLink);
        }
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
