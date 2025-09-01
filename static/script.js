document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resume-form');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const previewFrame = document.getElementById('resume-preview');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const downloadDocxBtn = document.getElementById('download-docx-btn');
    const submitBtn = document.getElementById('submit-btn');
    const loadingMessage = document.getElementById('loading-message');
    const resumeFileInput = document.getElementById('resume');

    // Prevent zoom on focus for iOS
    const preventZoom = (e) => {
        e.target.style.fontSize = '16px';
    };
    
    document.querySelectorAll('input[type="url"], input[type="file"]').forEach(input => {
        input.addEventListener('focus', preventZoom);
    });

    const messages = [
        "Extracting content from your resume...",
        "Analyzing the job requirements...",
        "AI is tailoring your content for this role...",
        "Creating professional formatting...",
        "Finalizing your job-ready resume..."
    ];

    let intervalId;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const jobUrl = document.getElementById('jobUrl').value;
        const resumeFile = resumeFileInput.files[0];

        if (!resumeFile) {
            alert('Please select a resume file.');
            return;
        }

        // --- UI updates for loading state ---
        resultsDiv.classList.add('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating...';
        loadingDiv.classList.remove('hidden');
        
        let messageIndex = 0;
        loadingMessage.textContent = messages[messageIndex];
        intervalId = setInterval(() => {
            messageIndex = (messageIndex + 1) % messages.length;
            loadingMessage.textContent = messages[messageIndex];
        }, 3000);

        try {
            const formData = new FormData();
            formData.append('jobUrl', jobUrl);
            formData.append('resumeFile', resumeFile);

            const response = await fetch('/generate', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            console.log('DEBUG: Backend response:', data);

            if (!response.ok) {
                throw new Error(data.error || 'An unknown server error occurred');
            }

            if (!data.preview_url) {
                throw new Error('Server response missing preview URL');
            }

            const previewUrl = data.preview_url;
            const docxUrl = data.docx_url;
            const explanation = data.explanation;
            console.log('DEBUG: Preview URL:', previewUrl);
            if (docxUrl) {
                console.log('DEBUG: DOCX URL:', docxUrl);
            }
            console.log('DEBUG: Explanation:', explanation);

            // Display the transformation explanation
            displayExplanation(explanation);

            // Add loading state for preview
            const previewContainer = document.querySelector('.preview-container');
            previewContainer.innerHTML = '<div style="display: flex; justify-content: center; align-items: center; height: 100%; font-size: 1.1rem; color: #6c757d;"><div>Loading resume preview...</div></div>';

            // Try to load PDF in iframe first, with improved fallback
            const checkAndDisplayPreview = () => {
                // Check if mobile device
                const isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                
                if (isMobile) {
                    // Mobile devices often have issues with PDF iframes, show success message instead
                    showInlinePreview(previewUrl, previewContainer);
                } else {
                    // Desktop: try iframe first
                    previewContainer.innerHTML = `<iframe id="resume-preview" src="${previewUrl}#view=FitH&toolbar=1&navpanes=0&scrollbar=1&page=1&zoom=page-width" frameborder="0" style="width: 100%; height: 100%; border: 1px solid #dee2e6;" allowfullscreen></iframe>`;
                    
                    const newIframe = previewContainer.querySelector('iframe');
                    let iframeLoaded = false;
                    
                    // Fallback if iframe doesn't load within 3 seconds
                    setTimeout(() => {
                        if (!iframeLoaded) {
                            console.log('DEBUG: Iframe failed to load, showing inline preview');
                            showInlinePreview(previewUrl, previewContainer);
                        }
                    }, 3000);
                    
                    newIframe.onload = () => {
                        iframeLoaded = true;
                        console.log('DEBUG: Preview iframe loaded successfully');
                    };
                    
                    newIframe.onerror = () => {
                        console.log('DEBUG: Iframe error, showing inline preview');
                        showInlinePreview(previewUrl, previewContainer);
                    };
                }
            };

            // Add error handling for iframe load
            previewFrame.onerror = (error) => {
                console.error('Error loading preview:', error);
                showInlinePreview(previewUrl, previewContainer);
            };

            // Check and display preview
            checkAndDisplayPreview();
            
            // Set up download buttons
            downloadPdfBtn.href = previewUrl;
            document.getElementById('preview-link').href = previewUrl;
            console.log('DEBUG: Set PDF download button href to:', downloadPdfBtn.href);
            
            // Set up DOCX download if available
            if (docxUrl) {
                downloadDocxBtn.href = docxUrl;
                downloadDocxBtn.style.display = 'inline-block';
                console.log('DEBUG: Set DOCX download button href to:', downloadDocxBtn.href);
            } else {
                downloadDocxBtn.style.display = 'none';
            }
            
            // Verify the PDF exists by making a HEAD request
            fetch(previewUrl, { method: 'HEAD' })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('PDF file not found');
                    }
                    resultsDiv.classList.remove('hidden');
                    console.log('DEBUG: PDF verified and results shown');
                })
                .catch(error => {
                    console.error('Error verifying PDF:', error);
                    throw error;
                });

        } catch (error) {
            console.error('Error during generation:', error);
            alert(`An error occurred: ${error.message}. Please try again.`);
        } finally {
            clearInterval(intervalId);
            loadingDiv.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate My Tailored Resume';
        }
    });
});

function showInlinePreview(previewUrl, previewContainer) {
    // Check if mobile device
    const isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        previewContainer.innerHTML = `
            <div style="height: 100%; width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center;">
                <div style="font-size: 1.1rem; color: #28a745; margin-bottom: 15px;">✅ Resume Generated Successfully!</div>
                <div style="font-size: 0.9rem; color: #6c757d; margin-bottom: 20px; line-height: 1.4;">Your professional resume is ready! Use the download buttons below to get your PDF or editable Word document.</div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; width: 100%; max-width: 300px; margin-bottom: 15px;">
                    <div style="font-size: 0.85rem; color: #495057;">💡 Tip: Download the PDF for immediate job applications, or the Word doc to make further edits.</div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="${previewUrl}" target="_blank" style="color: #007bff; text-decoration: none; font-size: 0.9rem; padding: 8px 15px; border: 1px solid #007bff; border-radius: 5px; display: inline-block;">📄 Preview Resume</a>
                </div>
            </div>
        `;
    } else {
        // Desktop: Try different approaches for PDF display
        const embedHTML = `
            <div style="height: 100%; width: 100%; display: flex; flex-direction: column;">
                <div style="background: #f8f9fa; padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6; font-size: 0.9rem; color: #28a745;">
                    ✅ Resume Generated Successfully - Preview Below
                </div>
                <object data="${previewUrl}#view=FitH&toolbar=1" type="application/pdf" style="width: 100%; height: calc(100% - 80px); border: none;">
                    <embed src="${previewUrl}#view=FitH&toolbar=1" type="application/pdf" style="width: 100%; height: 100%;">
                        <div style="padding: 20px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <div style="font-size: 1.1rem; color: #28a745; margin-bottom: 15px;">✅ Resume Generated Successfully!</div>
                            <div style="font-size: 0.9rem; color: #6c757d; margin-bottom: 20px;">PDF preview not available in this browser.</div>
                            <a href="${previewUrl}" target="_blank" style="color: #007bff; text-decoration: none; font-size: 1rem; padding: 10px 20px; border: 2px solid #007bff; border-radius: 5px; display: inline-block;">📄 Open Resume in New Tab</a>
                        </div>
                    </embed>
                </object>
                <div style="padding: 10px; text-align: center; background: #f8f9fa; border-top: 1px solid #dee2e6;">
                    <a href="${previewUrl}" target="_blank" style="color: #007bff; text-decoration: none; font-size: 0.9rem;">📄 Open in new tab if preview isn't working</a>
                </div>
            </div>
        `;
        
        previewContainer.innerHTML = embedHTML;
    }
}

function displayExplanation(explanation) {
    const explanationContent = document.getElementById('explanation-content');
    
    if (!explanation) {
        explanationContent.innerHTML = `
            <ul>
                <li>Resume content enhanced with professional language and improved structure</li>
                <li>Experience bullets strengthened with action verbs and quantified achievements</li>
                <li>Skills section reorganized for maximum impact and relevance</li>
                <li>Overall presentation upgraded to meet current professional standards</li>
            </ul>
        `;
        return;
    }

    // Clean up the explanation text and convert to HTML
    let cleanedExplanation = explanation
        .replace(/TRANSFORMATION_EXPLANATION:/gi, '')
        .replace(/EXPLANATION FOCUS:/gi, '')
        .trim();

    // Check if the explanation contains bullet points
    if (cleanedExplanation.includes('•') || cleanedExplanation.includes('*') || cleanedExplanation.includes('-')) {
        // Convert bullet points to HTML list
        const lines = cleanedExplanation.split('\n');
        let htmlContent = '<ul>';
        
        for (let line of lines) {
            line = line.trim();
            if (line) {
                // Remove bullet characters and add as list item
                line = line.replace(/^[•\*\-]\s*/, '');
                if (line) {
                    htmlContent += `<li>${line}</li>`;
                }
            }
        }
        
        htmlContent += '</ul>';
        explanationContent.innerHTML = htmlContent;
    } else {
        // Convert to paragraphs if no bullet points
        const paragraphs = cleanedExplanation.split('\n\n');
        let htmlContent = '';
        
        for (let para of paragraphs) {
            para = para.trim();
            if (para) {
                htmlContent += `<p>${para}</p>`;
            }
        }
        
        explanationContent.innerHTML = htmlContent || '<p>Your resume has been enhanced with professional formatting and improved content structure.</p>';
    }
}