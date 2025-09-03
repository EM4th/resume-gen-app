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

            console.log('Success! Creating complete result display...');
            console.log('Data received:', data);
            
            // Hide loading and upload section
            loadingDiv.style.display = 'none';
            uploadSection.style.display = 'none';
            
            // Create comprehensive result display with explanation, preview, and download
            successDiv.innerHTML = `
                <div style="max-width: 1000px; margin: 0 auto; padding: 20px;">
                    <!-- Header -->
                    <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
                        <h2 style="margin: 0 0 10px 0; font-size: 28px;">🎉 Your Enhanced Resume is Ready!</h2>
                        <p style="margin: 0; font-size: 16px; opacity: 0.9;">AI has successfully optimized your resume for this job opportunity</p>
                    </div>
                    
                    <!-- Explanation Section -->
                    <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 25px; margin-bottom: 30px;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 20px;">📝 What We Improved</h3>
                        <div style="color: #495057; line-height: 1.6; font-size: 15px;">
                            ${data.explanation || 'Your resume has been enhanced to better match the job requirements.'}
                        </div>
                    </div>
                    
                    <!-- Preview and Download Section -->
                    <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 25px;">
                        <h3 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 20px;">📄 Your Enhanced Resume</h3>
                        
                        <!-- Preview Frame -->
                        <div style="text-align: center; margin-bottom: 25px;">
                            <iframe src="${data.preview_url}" 
                                    style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px;"
                                    title="Resume Preview">
                            </iframe>
                        </div>
                        
                        <!-- Action Buttons -->
                        <div style="text-align: center; margin-bottom: 20px;">
                            <a href="${data.preview_url}" 
                               target="_blank"
                               style="
                                   display: inline-block;
                                   padding: 12px 24px;
                                   background: #28a745;
                                   color: white;
                                   text-decoration: none;
                                   border-radius: 6px;
                                   font-weight: 600;
                                   margin: 0 10px;
                                   transition: background 0.3s;
                               "
                               onmouseover="this.style.background='#218838'"
                               onmouseout="this.style.background='#28a745'">
                                👀 Open Full Preview
                            </a>
                            
                            <a href="${data.download_url || data.preview_url}" 
                               download="enhanced_resume.pdf"
                               style="
                                   display: inline-block;
                                   padding: 12px 24px;
                                   background: #007bff;
                                   color: white;
                                   text-decoration: none;
                                   border-radius: 6px;
                                   font-weight: 600;
                                   margin: 0 10px;
                                   transition: background 0.3s;
                               "
                               onmouseover="this.style.background='#0056b3'"
                               onmouseout="this.style.background='#007bff'">
                                📥 Download PDF
                            </a>
                        </div>
                        
                        <!-- New Resume Button -->
                        <div style="text-align: center; padding-top: 20px; border-top: 1px solid #e9ecef;">
                            <button onclick="location.reload()" 
                                    style="
                                        padding: 10px 20px;
                                        background: #6c757d;
                                        color: white;
                                        border: none;
                                        border-radius: 6px;
                                        cursor: pointer;
                                        font-weight: 600;
                                        transition: background 0.3s;
                                    "
                                    onmouseover="this.style.background='#545b62'"
                                    onmouseout="this.style.background='#6c757d'">
                                📄 Create Another Resume
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            // Show success container
            successDiv.style.display = 'block';
            
            console.log('Complete result display created successfully');

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
