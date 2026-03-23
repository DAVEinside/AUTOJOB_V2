# Resume & Cover Letter Tailoring System

An AI-powered Python system that customizes your resume and generates personalized cover letters for specific job descriptions while **preserving your original document formatting**.

## 🎯 Features

- **Smart Resume Tailoring**: Automatically adapts your resume to match job descriptions
- **Format Preservation**: Maintains exact margins, fonts, and styling from your original document
- **Personalized Cover Letters**: Generates unique, story-driven cover letters (not just resume rephrasing)
- **ATS Optimization**: Incorporates relevant keywords for Applicant Tracking Systems
- **One-Page Guarantee**: Ensures tailored content fits within page limits
- **PDF Output**: Generates print-ready PDF files

## 📁 Project Structure

```
resume_tailor/
├── main.py                    # CLI orchestrator
├── config.py                  # Configuration and settings
├── llm_processor.py           # AI content generation
├── resume_editor.py           # Document manipulation
├── cover_letter_generator.py  # Cover letter creation
├── requirements.txt           # Dependencies
├── templates/                 # Document templates
└── output/                    # Generated files
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### 3. Run the System

**Interactive Mode:**
```bash
python main.py
```

**With Job Description File:**
```bash
python main.py --file job_description.txt
```

**Direct Input:**
```bash
python main.py --jd "Full job description text here..."
```

## 📋 Usage Examples

### Basic Usage
```bash
python main.py
# Then paste the job description when prompted
```

### Specify Output Directory
```bash
python main.py --file jd.txt --output ./applications/google/
```

### With Custom API Key
```bash
python main.py --api-key sk-ant-xxx --file jd.txt
```

## 🔧 Configuration

Edit `config.py` to customize:

- **Personal Information**: Name, contact details, education
- **Editable Sections**: Which parts of the resume to modify
- **Character Limits**: Maximum lengths for bullets, summary
- **LLM Settings**: Model, temperature, token limits

## 📄 Sections Modified

The system modifies these resume sections:

1. **Professional Summary** - Rewritten to align with job requirements
2. **Sirch (AI Engineer)** - Bullet points tailored to target role
3. **Blockhouse (ML Engineer)** - Bullet points tailored to target role
4. **Skills** - Reordered and optimized for ATS

**NOT Modified** (preserved as-is):
- Education section
- Other work experiences
- Projects section
- Contact information
- Document formatting

## 🛡️ Ethical Guidelines

This system follows strict ethical boundaries:

✅ **What it does:**
- Reframes existing experiences with relevant keywords
- Highlights skills that match the job
- Reorganizes content for relevance

❌ **What it won't do:**
- Fabricate experiences or skills
- Add qualifications you don't have
- Create misleading claims

## 📊 Output Files

Generated files follow this naming convention:

```
output/
├── Nimit_Resume_CompanyName.pdf      # Tailored resume
└── CoverLetter_CompanyName.pdf       # Personalized cover letter
```

## 🔌 System Requirements

- Python 3.8+
- LibreOffice (for PDF conversion)
- Anthropic API access

### Installing LibreOffice

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice
```

**macOS:**
```bash
brew install --cask libreoffice
```

**Windows:**
Download from https://www.libreoffice.org/download/

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py (CLI)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │  llm_processor  │  │        resume_editor            │  │
│  │                 │  │                                 │  │
│  │ • Analyze JD    │  │ • Extract XML from DOCX         │  │
│  │ • Generate text │  │ • Edit text runs                │  │
│  │ • Tailor content│  │ • Preserve formatting           │  │
│  └────────┬────────┘  │ • Repack to DOCX               │  │
│           │           │ • Convert to PDF                │  │
│           ▼           └─────────────────────────────────┘  │
│  ┌─────────────────┐                                       │
│  │ cover_letter    │                                       │
│  │ _generator      │                                       │
│  │                 │                                       │
│  │ • Generate HTML │                                       │
│  │ • Convert PDF   │                                       │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### PDF Conversion Fails
Ensure LibreOffice is installed and `soffice` is in your PATH.

### API Key Issues
- Check that `ANTHROPIC_API_KEY` is set correctly
- Verify your API key has sufficient credits

### Formatting Lost
The system edits XML directly to preserve formatting. If issues occur:
1. Ensure the source DOCX isn't corrupted
2. Check that Word/LibreOffice can open the original

## 📝 License

MIT License - Feel free to use and modify for your job search!

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows existing patterns
- Tests pass
- Documentation is updated

---

*Built with ❤️ using Claude and Anthropic's API*
