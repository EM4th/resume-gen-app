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
        
        console.log('Starting resume generation...');

        try {
            const formData = new FormData();
            formData.append('job_description', jobDescription);
            formData.append('resume_file', resumeFile);
            formData.append('format', format);

            console.log('Submitting form data...');
            
            const response = await fetch('/generate_resume', {
                method: 'POST',
                body: formData,
            });

            console.log('Response status:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);

            if (!response.ok) {
                throw new Error(data.error || 'Server error occurred');
            }

            if (!data.success) {
                throw new Error(data.error || 'Resume generation failed');
            }

            console.log('Success! Creating result display...');
            
            // Hide loading
            loadingDiv.style.display = 'none';
            
            // Create comprehensive result display with explanation, preview, and download
            const extra = data.additional_downloads || {};
            const docxLink = extra.docx ? `<a href="${extra.docx}" download="enhanced_resume.docx" style="display: inline-block; padding: 12px 24px; background: #6f42c1; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 0 10px; transition: background 0.3s;" onmouseover="this.style.background='#59359a'" onmouseout="this.style.background='#6f42c1'">📝 Download DOCX</a>` : '';
            const jobUrlNote = data.job_url ? `<p style="margin-top:6px; font-size:13px; color:#666;">Analyzed job source: <a href="${data.job_url}" target="_blank" rel="noopener">${data.job_url}</a></p>` : '';

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
                        ${jobUrlNote}
                        <div style="color: #495057; line-height: 1.6; font-size: 15px;">
                            ${data.explanation || 'Your resume has been enhanced to better match the job requirements.'}
                        </div>
                    </div>
                    
                    <!-- Preview and Download Section -->
                    <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 25px;">
                        <h3 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 20px;">📄 Your Enhanced Resume</h3>
                        
                        <!-- Preview Frame -->
                        <div style="text-align: center; margin-bottom: 25px;">
                            <iframe src="${data.preview_url || data.download_url}" 
                                    style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px;"
                                    title="Resume Preview">
                            </iframe>
                        </div>
                        
                        <!-- Action Buttons -->
                        <div style="text-align: center; margin-bottom: 20px;">
                            <a href="${data.preview_url || data.download_url}" 
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
                            ${docxLink}
                        </div>
                        
                        <!-- New Resume Button -->
                        <div style="text-align: center; padding-top: 20px; border-top: 1px solid #e9ecef;">
                            <button onclick="createNewResume()" 
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
            
            console.log('Result display created successfully');

        } catch (error) {
            console.error('Error:', error);
            
            // Hide loading and show upload section again
            loadingDiv.style.display = 'none';
            uploadSection.style.display = 'block';
            
            // Show error message
            alert(`Error: ${error.message}`);
            
        } finally {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.textContent = '🎯 Generate Enhanced Resume';
        }
    });
});
