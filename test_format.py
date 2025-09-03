import os
import pdfplumber
from app import final_format_resume, create_pdf_resume, sanitize_enhanced_content

RAW_SAMPLE = """- *John Smith**\n- john.smith@email.com | (555) 123-4567 | linkedin.com/in/johnsmith\n- *Summary**\nExperienced product manager driving cross-functional teams to deliver SaaS features. increased retention 15%.\n- optimized onboarding flows reducing churn.\nEXPERIENCE\nAcme Corp – Senior Product Manager | 2021 - Present\nLed roadmap execution across engineering & design. boosted NPS 12 points.\nManaged backlog; aligned stakeholders.\nProjects\nInternal Analytics Revamp – delivered modular dashboards; cut query time 40%.\nEducation\nB.S. Computer Science, University of Somewhere\nSkills\nPython, SQL, Roadmapping, A/B Testing, User Research, Agile, Jira\nCertifications\nPMP, CSM\n"""

# Simulate AI output cleaning pipeline
sanitized = sanitize_enhanced_content(RAW_SAMPLE)
formatted = final_format_resume(sanitized)

out_path = os.path.join('previews','test_format.pdf')
create_pdf_resume(formatted, out_path)
print('Generated:', out_path)

# Extract text to verify ordering
with pdfplumber.open(out_path) as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)
print('--- Extracted Text ---')
print(text)
