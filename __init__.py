"""
Resume & Cover Letter Tailoring System

A Python system for tailoring resumes and generating cover letters
based on job descriptions while preserving document formatting.
"""

__version__ = "1.0.0"
__author__ = "Nimit Dave"

from .config import PERSONAL_INFO, OUTPUT_DIR
from .llm_processor import LLMProcessor, TailoredContent
from .resume_editor import ResumeEditor, convert_to_pdf
from .cover_letter_generator import CoverLetterGenerator

__all__ = [
    'LLMProcessor',
    'TailoredContent', 
    'ResumeEditor',
    'CoverLetterGenerator',
    'convert_to_pdf',
    'PERSONAL_INFO',
    'OUTPUT_DIR'
]
