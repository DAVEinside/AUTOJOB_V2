#!/usr/bin/env python3
"""
Resume & Cover Letter Tailoring System
Main CLI Interface - CONTINUOUS MODE

Keeps running until you type 'quit', 'exit', or 'stop'
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT_DIR, RESUME_TEMPLATE, PERSONAL_INFO
from llm_processor import LLMProcessor, TailoredContent, get_current_resume_text
from resume_editor import ResumeEditor, convert_to_pdf, sanitize_filename
from cover_letter_generator import CoverLetterGenerator, generate_cover_letter_pdf
from dotenv import load_dotenv
import os
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def print_banner():
    """Print the application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║        RESUME & COVER LETTER TAILORING SYSTEM v2.0            ║
║              Continuous Mode - Process Multiple JDs           ║
╠═══════════════════════════════════════════════════════════════╣
║  Type 'quit', 'exit', or 'stop' to end the session            ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_divider():
    print("\n" + "=" * 63 + "\n")


def get_job_description_interactive() -> str:
    """Get job description through interactive input or stdin pipe"""
    print("📋 Paste the job description below.")
    print("   (Press Enter twice when done, or type 'quit' to exit)\n")
    print("-" * 60)
    
    lines = []
    empty_count = 0
    
    # Detect if running from pipe (non-interactive)
    is_pipe = not sys.stdin.isatty()
    
    while True:
        try:
            line = input()
            
            # Check for exit commands
            if line.strip().lower() in ['quit', 'exit', 'stop', 'q']:
                return None
            
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
                
        except EOFError:
            # When piped, EOF means end of input — return whatever we have
            break
    
    result = "\n".join(lines).strip()
    
    # If piped and got content, return it
    # If piped and empty, return None to exit
    if not result and is_pipe:
        return None
        
    return result if result else None


def process_single_jd(
    jd: str,
    llm: LLMProcessor,
    output_dir: Path,
    job_number: int = 1
) -> dict:
    """
    Process a single job description
    
    Returns:
        Dictionary with paths to generated files
    """
    print(f"\n🚀 Processing Job #{job_number}...")
    
    # Get current resume text for LLM
    current_resume = get_current_resume_text()
    
    # Generate all tailored content using prompt.txt
    print("   📊 Generating tailored content...")
    tailored = llm.generate_full_tailored_content(jd, current_resume)
    
    company_name = tailored.company_name
    job_title = tailored.job_title
    safe_company = sanitize_filename(company_name)
    
    print(f"   🎯 Target: {job_title} at {company_name}")
    
    # Create output paths
    resume_docx = output_dir / f"Nimit_Resume_{safe_company}.docx"
    resume_pdf = output_dir / f"Nimit_Resume_{safe_company}.pdf"
    cover_letter_pdf = output_dir / f"CoverLetter_{safe_company}.pdf"
    
    # Apply tailored content to resume
    print("   📝 Applying changes to resume...")
    editor = ResumeEditor(RESUME_TEMPLATE)
    editor.apply_tailored_content(
        sirch_bullets=tailored.sirch_bullets,
        blockhouse_bullets=tailored.blockhouse_bullets,
        washino_bullets=tailored.washino_bullets,
        skills=tailored.skills,
        output_docx_path=resume_docx
    )
    
    # Convert to PDF
    print("   📄 Converting to PDF...")
    try:
        convert_to_pdf(resume_docx, resume_pdf)
        resume_output = resume_pdf
    except Exception as e:
        print(f"   ⚠️  PDF conversion issue: {e}")
        resume_output = resume_docx
    
    # Generate cover letter
    print("   ✉️  Creating cover letter...")
    cover_letter_output = generate_cover_letter_pdf(
        cover_letter_text=tailored.cover_letter,
        company_name=company_name,
        job_title=job_title,
        output_path=cover_letter_pdf
    )
    
    # Print summary
    print("\n   ✅ DONE!")
    print(f"   📁 Resume: {resume_output.name}")
    print(f"   📁 Cover Letter: {cover_letter_output.name}")
    print(f"   🔑 Keywords: {', '.join(tailored.keywords_used[:6])}")
    
    return {
        "resume": resume_output,
        "cover_letter": cover_letter_output,
        "company_name": company_name,
        "job_title": job_title
    }


def run_continuous_mode(api_key: str = None, output_dir: Path = None):
    """
    Run in continuous mode - keep processing JDs until user quits
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize LLM processor once
    print("🔧 Initializing AI processor...")
    llm = LLMProcessor(api_key=ANTHROPIC_API_KEY)
    
    job_count = 0
    results = []
    
    print("\n✅ Ready! Paste job descriptions one at a time.\n")
    
    while True:
        print_divider()
        
        # Get JD from user
        jd = get_job_description_interactive()
        
        # Check for exit
        if jd is None:
            print("\n👋 Exiting... Thank you for using the Resume Tailor!")
            break
        
        if len(jd) < 50:
            print("⚠️  Job description too short. Please paste a complete JD.")
            continue
        
        job_count += 1
        
        try:
            result = process_single_jd(jd, llm, output_dir, job_count)
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error processing job #{job_count}: {e}")
            import traceback
            traceback.print_exc()
            print("\nContinuing to next job...")
            continue
    
    # Final summary
    if results:
        print_divider()
        print(f"📊 SESSION SUMMARY: Processed {len(results)} job(s)")
        print(f"📁 Output directory: {output_dir}")
        print("\nGenerated files:")
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r['job_title']} at {r['company_name']}")
            print(f"      • {r['resume'].name}")
            print(f"      • {r['cover_letter'].name}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Tailor resumes and generate cover letters (continuous mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The system runs continuously - paste JDs one by one.
Type 'quit', 'exit', or 'stop' to end the session.
        """
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=str(OUTPUT_DIR),
        help=f'Output directory (default: {OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--api-key', '-k',
        type=str,
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Get API key
    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("⚠️  No API key provided")
        print("   Set ANTHROPIC_API_KEY or use --api-key flag")
        print("   Attempting default configuration...\n")
    
    try:
        run_continuous_mode(
            api_key=api_key,
            output_dir=Path(args.output)
        )
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()