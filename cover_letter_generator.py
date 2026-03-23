"""
Cover Letter Generator Module
Creates personalized cover letters as PDF documents
"""
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from config import PERSONAL_INFO, OUTPUT_DIR


class CoverLetterGenerator:
    """Generates personalized cover letters"""
    
    def __init__(self):
        """Initialize the cover letter generator"""
        self.personal_info = PERSONAL_INFO
    
    def generate_html(
        self,
        cover_letter_text: str,
        company_name: str,
        job_title: str
    ) -> str:
        """
        Generate HTML for the cover letter
        
        Args:
            cover_letter_text: The generated cover letter content
            company_name: Target company name
            job_title: Target job title
            
        Returns:
            HTML string
        """
        today = datetime.now().strftime("%B %d, %Y")
        
        # Clean up the cover letter text - remove redundant greetings and closings
        cleaned_text = self._clean_cover_letter_content(cover_letter_text)
        
        # Parse the cover letter into paragraphs
        paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
        paragraphs_html = '\n'.join([f'<p>{p}</p>' for p in paragraphs])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cover Letter - {self.personal_info['name']}</title>
    <style>
        @page {{
            size: letter;
            margin: 1in;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.75in;
        }}
        
        .header {{
            margin-bottom: 24px;
        }}
        
        .name {{
            font-size: 18pt;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 4px;
        }}
        
        .contact-info {{
            font-size: 10pt;
            color: #555;
        }}
        
        .contact-info a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        .date {{
            margin: 24px 0;
        }}
        
        .recipient {{
            margin-bottom: 20px;
        }}
        
        .salutation {{
            margin-bottom: 16px;
        }}
        
        .body p {{
            margin-bottom: 14px;
            text-align: justify;
        }}
        
        .closing {{
            margin-top: 20px;
        }}
        
        .signature {{
            margin-top: 24px;
        }}
        
        .signature-name {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{self.personal_info['name']}</div>
        <div class="contact-info">
            {self.personal_info['location']} | 
            {self.personal_info['phone']} | 
            <a href="mailto:{self.personal_info['email']}">{self.personal_info['email']}</a> | 
            <a href="https://{self.personal_info['linkedin']}">LinkedIn</a> | 
            <a href="https://{self.personal_info['github']}">GitHub</a>
        </div>
    </div>
    
    <div class="date">{today}</div>
    
    <div class="recipient">
        <div>Hiring Manager</div>
        <div>{company_name}</div>
        <div>Re: {job_title} Position</div>
    </div>
    
    <div class="salutation">Dear Hiring Team,</div>
    
    <div class="body">
        {paragraphs_html}
    </div>
    
    <div class="closing">Sincerely,</div>
    
    <div class="signature">
        <div class="signature-name">{self.personal_info['name']}</div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_as_html(
        self,
        cover_letter_text: str,
        company_name: str,
        job_title: str,
        output_path: Path
    ) -> Path:
        """
        Save cover letter as HTML file
        
        Args:
            cover_letter_text: The generated cover letter content
            company_name: Target company name
            job_title: Target job title
            output_path: Path for output HTML
            
        Returns:
            Path to created HTML file
        """
        html = self.generate_html(cover_letter_text, company_name, job_title)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def convert_to_pdf(self, html_path: Path, pdf_path: Path) -> Path:
        """
        Convert HTML cover letter to PDF
        
        Args:
            html_path: Path to HTML file
            pdf_path: Path for output PDF
            
        Returns:
            Path to created PDF
        """
        # Try using wkhtmltopdf first
        try:
            cmd = ['wkhtmltopdf', '--enable-local-file-access', str(html_path), str(pdf_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and pdf_path.exists():
                return pdf_path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback to LibreOffice
        try:
            output_dir = pdf_path.parent
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(html_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            generated_pdf = output_dir / (html_path.stem + '.pdf')
            if generated_pdf.exists() and generated_pdf != pdf_path:
                os.rename(generated_pdf, pdf_path)
            
            return pdf_path
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"Warning: PDF conversion failed: {e}")
            return html_path  # Return HTML if PDF fails
    
    def create_cover_letter(
        self,
        cover_letter_text: str,
        company_name: str,
        job_title: str,
        output_dir: Optional[Path] = None,
        filename_prefix: str = "CoverLetter"
    ) -> Dict[str, Path]:
        """
        Create cover letter in both HTML and PDF formats
        
        Args:
            cover_letter_text: The generated cover letter content
            company_name: Target company name
            job_title: Target job title
            output_dir: Directory for output files
            filename_prefix: Prefix for output filenames
            
        Returns:
            Dictionary with paths to created files
        """
        if output_dir is None:
            output_dir = OUTPUT_DIR
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize company name for filename
        safe_company = self._sanitize_filename(company_name)
        
        # Generate HTML
        html_path = output_dir / f"{filename_prefix}_{safe_company}.html"
        self.save_as_html(cover_letter_text, company_name, job_title, html_path)
        
        # Convert to PDF
        pdf_path = output_dir / f"{filename_prefix}_{safe_company}.pdf"
        pdf_result = self.convert_to_pdf(html_path, pdf_path)
        
        # Clean up HTML if PDF was successful
        if pdf_result.suffix == '.pdf' and pdf_result.exists():
            try:
                html_path.unlink()
            except:
                pass
            return {'pdf': pdf_result}
        
        return {'html': html_path, 'pdf': pdf_result if pdf_result.exists() else None}
    
    def _clean_cover_letter_content(self, content: str) -> str:
        """
        Clean up LLM-generated cover letter content by removing redundant 
        greetings, closings, and fixing placeholders
        """
        import re
        
        # Replace placeholder names
        cleaned = content.replace('[Your Name]', 'Nimit Dave')
        
        # Remove common greeting patterns at the start
        greeting_patterns = [
            r'^Dear\s+[^,]*,?\s*',  # Any "Dear ..." at start
            r'^Hi\s+[^,]*,?\s*',    # Any "Hi ..." at start
            r'^Hello\s+[^,]*,?\s*'  # Any "Hello ..." at start
        ]
        
        for pattern in greeting_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove common closing patterns at the end
        closing_patterns = [
            r'\n*\s*(Best regards?|Sincerely|Yours truly|Kind regards?|Regards),?\s*\n*\[?Your Name\]?\s*$',
            r'\n*\s*(Best regards?|Sincerely|Yours truly|Kind regards?|Regards),?\s*\n*Nimit Dave\s*$',
            r'\n*\s*(Best regards?|Sincerely|Yours truly|Kind regards?|Regards),?\s*$'
        ]
        
        for pattern in closing_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Max 2 newlines
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _sanitize_filename(self, name: str) -> str:
        """Create a safe filename from a string"""
        import re
        safe = re.sub(r'[^\w\s-]', '', name)
        safe = re.sub(r'\s+', '_', safe)
        return safe[:50]


def generate_cover_letter_pdf(
    cover_letter_text: str,
    company_name: str,
    job_title: str,
    output_path: Path
) -> Path:
    """
    Convenience function to generate a cover letter PDF
    
    Args:
        cover_letter_text: The generated cover letter content
        company_name: Target company name
        job_title: Target job title
        output_path: Full path for output PDF
        
    Returns:
        Path to created file
    """
    generator = CoverLetterGenerator()
    
    html_path = output_path.with_suffix('.html')
    generator.save_as_html(cover_letter_text, company_name, job_title, html_path)
    
    result = generator.convert_to_pdf(html_path, output_path)
    
    # Clean up HTML if PDF successful
    if result.suffix == '.pdf' and html_path.exists():
        try:
            html_path.unlink()
        except:
            pass
    
    return result