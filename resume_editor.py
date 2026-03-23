"""
Resume Editor Module
Handles docx manipulation using XML editing to preserve formatting
NO SUMMARY SECTION - removed per requirements
"""
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import zipfile
from xml.etree import ElementTree as ET

from config import OUTPUT_DIR, RESUME_TEMPLATE, MAX_BULLET_CHARS, MAX_SKILLS_LINE_CHARS


# XML Namespaces for Word documents
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
}

for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


class ResumeEditor:
    """Handles Word document editing while preserving formatting"""
    
    def __init__(self, template_path: str = None):
        self.template_path = Path(template_path) if template_path else RESUME_TEMPLATE
        self.temp_dir = None
        self.document_tree = None
        
    def _extract_docx(self, docx_path: Path) -> Path:
        """Extract docx to temporary directory"""
        self.temp_dir = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        return self.temp_dir
    
    def _pack_docx(self, output_path: Path) -> None:
        """Repack the temporary directory into a docx file"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.temp_dir)
                    zipf.write(file_path, arcname)
    
    def _load_document_xml(self) -> ET.Element:
        """Load and parse document.xml"""
        doc_path = self.temp_dir / "word" / "document.xml"
        self.document_tree = ET.parse(doc_path)
        return self.document_tree.getroot()
    
    def _save_document_xml(self) -> None:
        """Save modified document.xml"""
        doc_path = self.temp_dir / "word" / "document.xml"
        with open(doc_path, 'wb') as f:
            self.document_tree.write(f, encoding='UTF-8', xml_declaration=True)
    
    def _get_text_content(self, element: ET.Element) -> str:
        """Extract all text content from an XML element"""
        texts = []
        for t_elem in element.iter('{%s}t' % NAMESPACES['w']):
            if t_elem.text:
                texts.append(t_elem.text)
        return ''.join(texts)
    
    def _find_paragraphs_after_marker(self, root: ET.Element, marker_text: str, count: int) -> List[ET.Element]:
        """Find bullet point paragraphs after a marker text"""
        paragraphs = list(root.iter('{%s}p' % NAMESPACES['w']))
        result = []
        found_marker = False
        
        for p in paragraphs:
            text = self._get_text_content(p)
            if marker_text.lower() in text.lower():
                found_marker = True
                continue
            if found_marker and len(result) < count:
                # Check if this is a bullet point (has numPr)
                if p.find('.//{%s}numPr' % NAMESPACES['w']) is not None:
                    result.append(p)
        
        return result
    
    def _find_washino_paragraphs(self, root: ET.Element, count: int) -> List[ET.Element]:
        """Find Washino bullet point paragraphs specifically"""
        paragraphs = list(root.iter('{%s}p' % NAMESPACES['w']))
        result = []
        washino_found = False
        blockhouse_found = False
        
        for p in paragraphs:
            text = self._get_text_content(p)
            
            # First find Washino company marker
            if "Washino" in text:
                washino_found = True
                continue
                
            # If we're in Washino section and find ML Engineer, skip it (this is the title)
            if washino_found and ("Machine Learning Engineer" in text or "Machine Learning Enginee" in text):
                continue
                
            # Now collect bullet points for Washino
            if washino_found and len(result) < count:
                # Check if this is a bullet point (has numPr)
                if p.find('.//{%s}numPr' % NAMESPACES['w']) is not None:
                    result.append(p)
        
        return result
    
    def _clear_paragraph_text(self, paragraph: ET.Element) -> None:
        """Clear all text from a paragraph"""
        for run in paragraph.findall('.//{%s}r' % NAMESPACES['w']):
            for t_elem in run.findall('{%s}t' % NAMESPACES['w']):
                t_elem.text = ''
    
    def _update_paragraph_with_formatted_text(self, paragraph: ET.Element, new_text: str) -> None:
        """Update paragraph with text, handling **bold** markers"""
        # Parse bold parts
        parts = self._extract_formatted_parts(new_text)
        
        # Get existing runs
        runs = list(paragraph.findall('{%s}r' % NAMESPACES['w']))
        
        # Clear existing text runs (but keep the first one for reference)
        text_runs = [r for r in runs if r.find('{%s}t' % NAMESPACES['w']) is not None]
        for run in text_runs[1:]:
            try:
                paragraph.remove(run)
            except ValueError:
                pass
        
        if not text_runs:
            return
        
        # Find insert position
        pPr = paragraph.find('{%s}pPr' % NAMESPACES['w'])
        insert_pos = list(paragraph).index(pPr) + 1 if pPr is not None else 0
        
        # Remove the first text run too
        if text_runs:
            try:
                paragraph.remove(text_runs[0])
            except ValueError:
                pass
        
        # Create new runs for each part
        for text_part, is_bold in parts:
            new_run = ET.Element('{%s}r' % NAMESPACES['w'])
            
            # Create run properties
            rPr = ET.SubElement(new_run, '{%s}rPr' % NAMESPACES['w'])
            sz = ET.SubElement(rPr, '{%s}sz' % NAMESPACES['w'])
            sz.set('{%s}val' % NAMESPACES['w'], '20')
            
            if is_bold:
                ET.SubElement(rPr, '{%s}b' % NAMESPACES['w'])
                ET.SubElement(rPr, '{%s}bCs' % NAMESPACES['w'])
            
            # Create text element
            t_elem = ET.SubElement(new_run, '{%s}t' % NAMESPACES['w'])
            t_elem.text = text_part
            t_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            
            paragraph.insert(insert_pos, new_run)
            insert_pos += 1
    
    def _extract_formatted_parts(self, text: str) -> List[Tuple[str, bool]]:
        """Extract text parts with bold markers (**text**)"""
        parts = []
        pattern = r'\*\*([^*]+)\*\*'
        last_end = 0
        
        for match in re.finditer(pattern, text):
            if match.start() > last_end:
                parts.append((text[last_end:match.start()], False))
            parts.append((match.group(1), True))
            last_end = match.end()
        
        if last_end < len(text):
            parts.append((text[last_end:], False))
        
        # If no bold found, return whole text as non-bold
        if not parts:
            parts = [(text, False)]
        
        return parts
    
    def _update_skills_section(self, root: ET.Element, new_skills: Dict[str, str]) -> None:
        """Update the entire skills section with new skills"""
        skills_section = False
        
        for p in root.iter('{%s}p' % NAMESPACES['w']):
            text = self._get_text_content(p)
            
            # Detect skills section start
            if "Skills" in text and len(text) < 20:
                skills_section = True
                continue
            
            if skills_section:
                # Match each category
                for category, skills_str in new_skills.items():
                    # Match by first word of category
                    category_start = category.split()[0]
                    if category_start in text and ":" in text:
                        self._update_skills_line(p, category, skills_str)
                        break
    
    def _update_skills_line(self, paragraph: ET.Element, category: str, skills: str) -> None:
        """Update a single skills line"""
        runs = list(paragraph.findall('{%s}r' % NAMESPACES['w']))
        
        # Find the non-bold run (skills content, not category name)
        for run in runs:
            rPr = run.find('{%s}rPr' % NAMESPACES['w'])
            is_bold = False
            if rPr is not None:
                b_elem = rPr.find('{%s}b' % NAMESPACES['w'])
                is_bold = b_elem is not None
            
            if not is_bold:
                t_elem = run.find('{%s}t' % NAMESPACES['w'])
                if t_elem is not None:
                    current = t_elem.text or ''
                    # Only update if it looks like skills content
                    if ',' in current or len(current) > 10:
                        t_elem.text = ' ' + skills
                        t_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                        return
    
    def apply_tailored_content(
        self,
        sirch_bullets: List[str],
        blockhouse_bullets: List[str],
        washino_bullets: List[str],
        skills: Dict[str, str],
        output_docx_path: Path
    ) -> Path:
        """
        Apply tailored content to the resume template
        NO SUMMARY - removed per requirements
        """
        # Extract fresh copy of template
        self._extract_docx(self.template_path)
        root = self._load_document_xml()
        
        # Update Sirch bullets (after "AI Developer" marker)
        print("   📝 Updating Sirch bullets...")
        sirch_paras = self._find_paragraphs_after_marker(root, "AI Developer", len(sirch_bullets))
        for para, bullet in zip(sirch_paras, sirch_bullets):
            self._update_paragraph_with_formatted_text(para, bullet)
        
        # Update Blockhouse bullets (after "Machine Learning Enginee" marker)
        print("   📝 Updating Blockhouse bullets...")
        blockhouse_paras = self._find_paragraphs_after_marker(root, "Machine Learning Enginee", len(blockhouse_bullets))
        for para, bullet in zip(blockhouse_paras, blockhouse_bullets):
            self._update_paragraph_with_formatted_text(para, bullet)
        
        # Update Washino bullets (after "Machine Learning Engineer" marker - but skip Blockhouse ones)
        print("   📝 Updating Washino bullets...")
        # We need to find the second occurrence of "Machine Learning Engineer" (after Blockhouse)
        washino_paras = self._find_washino_paragraphs(root, len(washino_bullets))
        for para, bullet in zip(washino_paras, washino_bullets):
            self._update_paragraph_with_formatted_text(para, bullet)
        
        # Update skills section
        print("   🔧 Updating skills section...")
        self._update_skills_section(root, skills)
        
        # Save document
        self._save_document_xml()
        
        # Pack into docx
        self._pack_docx(output_docx_path)
        
        # Clean up temp dir
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        return output_docx_path


def convert_to_pdf(docx_path: Path, output_pdf_path: Path) -> Path:
    """Convert docx to PDF using LibreOffice"""
    output_dir = output_pdf_path.parent
    
    cmd = [
        'soffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', str(output_dir),
        str(docx_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # LibreOffice creates PDF with same name as input
        generated_pdf = output_dir / (docx_path.stem + '.pdf')
        
        if generated_pdf.exists() and generated_pdf != output_pdf_path:
            shutil.move(generated_pdf, output_pdf_path)
        
        return output_pdf_path
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  PDF conversion timed out")
        return docx_path
    except FileNotFoundError:
        print("   ⚠️  LibreOffice not found, using DOCX")
        return docx_path


def sanitize_filename(name: str) -> str:
    """Create a safe filename from a string"""
    safe = re.sub(r'[^\w\s-]', '', name)
    safe = re.sub(r'\s+', '_', safe)
    return safe[:50]