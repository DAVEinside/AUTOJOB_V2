"""
Configuration file for Resume Tailor System
Contains personal details, API settings, and paths
"""
import os
from pathlib import Path

# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
UPLOADS_DIR = Path("/home/nimit/resume_tailor_system/uploads")

# Resume template paths
RESUME_TEMPLATE = TEMPLATE_DIR / "Nimit_Resume.docx"
PROMPT_FILE = TEMPLATE_DIR / "prompt.txt"

# Fallback to uploads if not in templates
if not RESUME_TEMPLATE.exists():
    RESUME_TEMPLATE = UPLOADS_DIR / "Nimit_Resume.docx"
if not PROMPT_FILE.exists():
    PROMPT_FILE = UPLOADS_DIR / "prompt.txt"

# ============================================================
# PERSONAL DETAILS (for cover letter generation)
# ============================================================
PERSONAL_INFO = {
    "name": "Nimit Dave",
    "phone": "(857)-397-2694",
    "email": "nimitdave3001@gmail.com",
    "linkedin": "https://www.linkedin.com/in/dave-inside/",
    "github": "https://github.com/DAVEinside",
    "location": "Boston, MA",
    "current_title": "Machine Learning Engineer",
    "years_experience": "3+",
    "education": {
        "masters": {
            "degree": "Master of Science in Data Analytics Engineering",
            "school": "Northeastern University",
            "location": "Boston, USA",
            "gpa": "3.8/4.0",
            "graduation": "May 2024"
        },
        "bachelors": {
            "degree": "Bachelor of Engineering in Mechanical Engineering",
            "school": "University of Mumbai",
            "location": "Mumbai, India",
            "gpa": "3.7/4.0",
            "graduation": "May 2022"
        }
    }
}

# ============================================================
# RESUME SECTIONS CONFIGURATION
# ============================================================
# Summary section REMOVED - no longer editing it
EDITABLE_SECTIONS = {
    "skills": True,
    "sirch_bullets": True,
    "blockhouse_bullets": True
}

# Companies whose bullet points should be rewritten
EDITABLE_COMPANIES = ["Sirch", "Blockhouse"]

# Skills categories to update
SKILLS_CATEGORIES = [
    "Languages & Core",
    "ML & AI Frameworks",
    "Big Data & Distributed Computing",
    "MLOps & Tools"
]

# ============================================================
# LLM CONFIGURATION
# ============================================================
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_TEMPERATURE = 0.3

MAX_TOKENS = {
    "full_resume": 4000,
    "bullet_point": 150,
    "skills": 500,
    "cover_letter": 1500
}

# ============================================================
# DOCUMENT CONSTRAINTS - CRITICAL FOR 1-PAGE FIT  
# ============================================================
MAX_BULLET_CHARS = 180  # Increased to allow 2-line bullets like reference
MAX_BULLETS_PER_COMPANY = {
    "Sirch": 4,
    "Blockhouse": 4,
    "Washino": 4
}
MAX_SKILLS_LINE_CHARS = 130  # Increased to utilize available space better

# ============================================================
# PDF / COVER LETTER SETTINGS
# ============================================================
PDF_SETTINGS = {"dpi": 300, "compress": True}
COVER_LETTER_SETTINGS = {
    "max_paragraphs": 4,
    "include_story": True,
    "tone": "professional_warm"
}