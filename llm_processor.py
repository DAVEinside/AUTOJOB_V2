"""
LLM Processor Module
Uses prompt.txt instructions to generate tailored resume content and cover letters
"""
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import anthropic

from config import (
    PERSONAL_INFO, LLM_MODEL, LLM_TEMPERATURE, MAX_TOKENS,
    MAX_BULLET_CHARS, MAX_SKILLS_LINE_CHARS, PROMPT_FILE
)


@dataclass
class TailoredContent:
    """Container for tailored resume content"""
    sirch_bullets: List[str]
    blockhouse_bullets: List[str]
    washino_bullets: List[str]
    skills: Dict[str, str]
    cover_letter: str
    company_name: str
    job_title: str
    keywords_used: List[str]


def load_prompt_instructions() -> str:
    """Load tailoring instructions from prompt.txt"""
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️  Warning: prompt.txt not found at {PROMPT_FILE}")
        return ""


class LLMProcessor:
    """Handles LLM interactions using prompt.txt instructions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM processor with Anthropic client"""
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.model = LLM_MODEL
        self.prompt_instructions = load_prompt_instructions()
    
    def generate_full_tailored_content(
        self, 
        jd: str, 
        current_resume: str
    ) -> TailoredContent:
        """
        Generate ALL tailored content using prompt.txt instructions
        This is the main method that uses prompt.txt to generate everything
        
        Args:
            jd: Job description text
            current_resume: Current resume content as text
            
        Returns:
            TailoredContent with all sections and cover letter
        """
        print("📊 Generating tailored content using prompt.txt instructions...")
        
        # Build the full prompt using prompt.txt
        full_prompt = f"""{self.prompt_instructions}

---

## CURRENT RESUME:
{current_resume}

---

## JOB DESCRIPTION:
{jd}

---

## OUTPUT INSTRUCTIONS:
Based on the above instructions and the job description, provide the tailored resume content and cover letter.

KEYWORD EXTRACTION PRIORITY:
1. Extract EVERY technical skill, tool, framework, language, and platform mentioned in the JD
2. Include industry buzzwords, methodologies, and specific technologies
3. Capture soft skills, certifications, and domain-specific terms
4. Ensure comprehensive coverage in the skills section

CONTENT MAXIMIZATION:
1. Create bullets that are close to the character limit but avoid line wrapping issues
2. Include specific metrics, technologies, and impact where possible
3. Use technical depth appropriate for startup experience levels
4. Ensure each bullet tells a complete story of achievement

Return your response in the following JSON format ONLY (no other text):
{{
    "company_name": "extracted company name",
    "job_title": "extracted job title",
    "keywords": ["keyword1", "keyword2", ...],
    "sirch_bullets": [
        "First tailored bullet for Sirch (AI Engineer role)",
        "Second tailored bullet for Sirch",
        "Third tailored bullet for Sirch"
    ],
    "blockhouse_bullets": [
        "First tailored bullet for Blockhouse (ML Engineer role)",
        "Second tailored bullet for Blockhouse",
        "Third tailored bullet for Blockhouse", 
        "Fourth tailored bullet for Blockhouse"
    ],
    "washino_bullets": [
        "First tailored bullet for Washino (Software Developer Intern role)",
        "Second tailored bullet for Washino",
        "Third tailored bullet for Washino",
        "Fourth tailored bullet for Washino"
    ],
    "skills": {{
        "Languages & Core": "skill1, skill2, skill3, ...",
        "ML & AI Frameworks": "skill1, skill2, skill3, ...",
        "Big Data & Distributed Computing": "skill1, skill2, ...",
        "MLOps & Tools": "skill1, skill2, skill3, ..."
    }},
    "cover_letter": "Full personalized cover letter text here (3-4 paragraphs, with a personal story, not just restating resume)"
}}

CRITICAL CONSTRAINTS:
- Each bullet point should be 140-170 characters for optimal space utilization (like the reference example)
- Each skills line MUST be under {MAX_SKILLS_LINE_CHARS} characters and include relevant JD keywords
- Sirch: exactly 4 bullets (substantial content, startup experience with technical depth and metrics)
- Blockhouse: exactly 4 bullets (substantial content, startup experience with business impact)
- Washino: exactly 4 bullets (shorter/simpler, junior-level contributions, around 100-130 chars)
- Cover letter: personalized with a story, NOT just resume rephrasing
- Use **bold** for 2-3 key technical terms per bullet, ensure complete sentences
- TARGET LENGTH: 140-170 characters per bullet for Sirch/Blockhouse, 100-130 for Washino
- COMPLETE SENTENCES ONLY: Every bullet must end naturally, no truncation or "..." endings
- AVOID sentence truncation: All bullets must be complete thoughts that end properly
- EXTRACT KEY KEYWORDS: Include important JD terms in skills section
- DO NOT fabricate - only reframe existing experience with appropriate detail"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS["full_resume"],
            temperature=LLM_TEMPERATURE,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        response_text = response.content[0].text.strip()
        
        # Parse JSON response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print("   Attempting fallback parsing...")
            data = self._fallback_parse(response_text)
        
        # Validate and trim content to fit page
        sirch_bullets = self._validate_bullets(data.get("sirch_bullets", []), 4)
        blockhouse_bullets = self._validate_bullets(data.get("blockhouse_bullets", []), 4)
        washino_bullets = self._validate_bullets(data.get("washino_bullets", []), 4)
        skills = self._validate_skills(data.get("skills", {}))
        
        return TailoredContent(
            sirch_bullets=sirch_bullets,
            blockhouse_bullets=blockhouse_bullets,
            washino_bullets=washino_bullets,
            skills=skills,
            cover_letter=data.get("cover_letter", ""),
            company_name=data.get("company_name", "Company"),
            job_title=data.get("job_title", "Position"),
            keywords_used=data.get("keywords", [])
        )
    
    def _validate_bullets(self, bullets: List[str], expected_count: int) -> List[str]:
        """Validate and trim bullets to fit constraints"""
        validated = []
        for bullet in bullets[:expected_count]:
            bullet = bullet.strip()
            # Remove leading dash if present
            if bullet.startswith("-"):
                bullet = bullet[1:].strip()
            # Trim if too long
            if len(bullet) > MAX_BULLET_CHARS:
                bullet = self._smart_trim(bullet, MAX_BULLET_CHARS)
            validated.append(bullet)
        
        # Pad with placeholders if not enough
        while len(validated) < expected_count:
            validated.append("Contributed to team projects and deliverables.")
        
        return validated
    
    def _validate_skills(self, skills: Dict[str, str]) -> Dict[str, str]:
        """Validate and trim skills to fit constraints"""
        validated = {}
        expected_categories = [
            "Languages & Core",
            "ML & AI Frameworks", 
            "Big Data & Cloud",
            "Web & APIs"
        ]
        
        for category in expected_categories:
            skill_line = skills.get(category, "")
            if len(skill_line) > MAX_SKILLS_LINE_CHARS:
                # Trim by removing skills from the end
                skill_list = [s.strip() for s in skill_line.split(",")]
                while len(", ".join(skill_list)) > MAX_SKILLS_LINE_CHARS and len(skill_list) > 2:
                    skill_list.pop()
                skill_line = ", ".join(skill_list)
            validated[category] = skill_line
        
        return validated
    
    def _smart_trim(self, text: str, max_len: int) -> str:
        """Intelligently trim text to max length, preferring complete sentences"""
        if len(text) <= max_len:
            return text
        
        # First try to find a natural sentence ending point
        sentence_endings = ['. ', '! ', '? ']
        best_cut = -1
        
        for ending in sentence_endings:
            pos = text.rfind(ending, 0, max_len - 10)  # Look for sentence ending before limit
            if pos > max_len // 2:  # Only if it's not too early
                best_cut = pos + 1
                break
        
        if best_cut > 0:
            return text[:best_cut].rstrip()
        
        # If no sentence ending found, try to cut at word boundary without adding "..."
        # Instead, just use a slightly higher character limit to avoid truncation
        if len(text) <= max_len + 20:  # If close to limit, allow slight overflow
            return text
        
        # Only if significantly over limit, cut at word boundary
        trimmed = text[:max_len-3]
        last_space = trimmed.rfind(" ")
        
        if last_space > max_len // 2:
            return text[:last_space].rstrip(".,;:")
        else:
            # If we must cut, do it cleanly without "..."
            return text[:max_len-10].rstrip(".,;: ")
    
    def _fallback_parse(self, text: str) -> Dict:
        """Fallback parsing when JSON fails"""
        return {
            "company_name": "Company",
            "job_title": "Position",
            "keywords": [],
            "sirch_bullets": [
                "Developed AI-powered Chrome extension with **Python FastAPI** and **LangChain**, serving **1,000+ daily users** with intelligent web summaries and automated content extraction",
                "Built full-stack architecture using **OpenAI APIs** (GPT-3.5, DALL-E), **JavaScript frontend** with async processing, and **Google Custom Search** integration",
                "Achieved **60% reduction in user comprehension time** through **NLP-powered summaries** and **AI-generated images** for complex web content transformation",
                "Implemented production infrastructure with **error handling**, **Redis caching**, **rate limiting**, and monitoring dashboards ensuring **99%+ uptime**"
            ],
            "blockhouse_bullets": [
                "Designed distributed **deep-learning trading system** using **PPO** and **Transformer architectures**, optimizing execution strategies on **AWS** for institutional clients",
                "Built **reinforcement learning pipelines** with **AWS Graviton processors**, reducing system latency by **25%** while processing **high-frequency trading data**",
                "Achieved **10% reduction in slippage**, **5% improvement in price impact**, and **12% reduction in transaction costs**, outperforming **TWAP/VWAP benchmarks**",
                "Led growth initiatives implementing **automated onboarding** and **personalized strategies**, onboarding **750+ users** and generating **$15,000 in revenue**"
            ],
            "washino_bullets": [
                "Built customer churn prediction models using **TensorFlow** and **PyTorch**, contributing to **20% increase in user retention**",
                "Assisted in developing **ETL pipelines** with **Apache Airflow** and **Kubernetes**, reducing data processing time by **30%**",
                "Supported **ML model deployment** on **AWS** using **MLflow** and **FastAPI** for real-time predictions",
                "Contributed to **CI/CD pipeline** development and automated testing for production systems"
            ],
            "skills": {
                "Languages & Core": "Python, JavaScript, TypeScript, SQL, C/C++, Java, Go, Bash, HTML/CSS, R",
                "ML & AI Frameworks": "PyTorch, TensorFlow, Keras, Scikit-Learn, XGBoost, Hugging Face Transformers, LangChain, OpenAI API, SpaCy, NLTK",
                "Big Data & Cloud": "AWS (EC2, S3, Lambda, SageMaker), GCP, Azure, Apache Spark, Kubernetes, Docker, Snowflake, Databricks, Hadoop",
                "Web & APIs": "FastAPI, Flask, Django, React, Node.js, REST APIs, GraphQL, WebSocket, Microservices, Nginx, Redis"
            },
            "cover_letter": text if len(text) > 200 else "Cover letter generation failed. Please regenerate."
        }
    
    def regenerate_cover_letter(
        self, 
        jd: str, 
        tailored_content: TailoredContent
    ) -> str:
        """
        Regenerate just the cover letter if needed
        """
        prompt = f"""{self.prompt_instructions}

Generate ONLY a personalized cover letter for this position.

JOB DESCRIPTION:
{jd}

CANDIDATE: {PERSONAL_INFO['name']}
TARGET: {tailored_content.job_title} at {tailored_content.company_name}

RELEVANT EXPERIENCE:
- At Sirch: {tailored_content.sirch_bullets[0] if tailored_content.sirch_bullets else 'AI engineering'}
- At Blockhouse: {tailored_content.blockhouse_bullets[0] if tailored_content.blockhouse_bullets else 'ML engineering'}

REQUIREMENTS:
- 3-4 paragraphs
- Include a personal/believable story showing problem-solving
- Professional but warm tone
- DO NOT just restate resume bullets
- Make it specific to this company

Write the cover letter now:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS["cover_letter"],
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()


def get_current_resume_text() -> str:
    """Get current resume content as structured text for the LLM"""
    return """
WORK EXPERIENCE:

Sirch | Boston, USA
AI Developer | November 2024 – Current
- Developed AI-powered Chrome extension with Python FastAPI backend and LangChain orchestration, serving 1,000+ daily users with intelligent web summaries and automated content extraction across diverse domains
- Built comprehensive full-stack architecture utilizing OpenAI APIs (GPT-3.5, DALL-E), JavaScript frontend with async processing, and Google Custom Search integration for enhanced user experience
- Achieved 60% reduction in user comprehension time through advanced NLP-powered 3-point summaries and contextually relevant AI-generated images for complex web content transformation
- Implemented robust production infrastructure with comprehensive error handling, Redis caching, rate limiting, and monitoring dashboards ensuring 99%+ uptime and sub-200ms response times

Blockhouse.app | NYC, USA
Machine Learning Engineer | June 2024 – November 2024
- Designed enterprise-grade distributed deep-learning multi-agent trading system using PPO and Transformer architectures, optimizing execution strategies on AWS infrastructure for institutional clients
- Built scalable reinforcement learning pipelines with AWS Graviton processors and GPU clusters, reducing system latency by 25% while processing high-frequency trading data at scale
- Achieved exceptional performance with 10% reduction in slippage, 5% improvement in price impact, and 12% reduction in transaction costs, consistently outperforming TWAP/VWAP benchmarks
- Led cross-functional growth initiatives implementing automated user onboarding and personalized strategies, successfully onboarding 750+ institutional users and generating $15,000 in revenue

KJSCE | Mumbai, India
Software Developer | September 2021 – May 2022
- Built a faculty portal for automatic summarization of 5,000+ academic documents using NLP and deep learning techniques.
- Implemented OCR-based data ingestion to digitize and automate database entry for 3,000+ scanned documents.
- Developed ML-based analysis tools for sentiment analysis, topic modeling, and text classification across 2,000 university publications.

Washino | Mumbai, India
Software Developer Intern | May 2020 – December 2021
- Built customer churn prediction models using TensorFlow and PyTorch, contributing to 20% increase in user retention
- Assisted in developing ETL pipelines with Apache Airflow and Kubernetes, reducing data processing time by 30%
- Supported ML model deployment on AWS using MLflow and FastAPI for real-time predictions
- Contributed to CI/CD pipeline development and automated testing for production systems

PROJECTS:

AI Agent Safety & Control Framework | Python, LangGraph, Docker | Dec 2025
- Engineered a “Ctrl-Z” safety protocol for autonomous agents using defer-to-resample and time-travel mechanisms to detect and revert adversarial actions.
- Improved agent safety scores to 70%+ from a 20–30% baseline while maintaining task utility.

Real-time AI-Powered Mathematical Analysis System | FastAPI, GPT-4o | June 2025
- Built a multimodal system for handwritten math problem solving with 95%+ accuracy and MathJax rendering.
- Implemented a responsive UI with live camera input, drag-and-drop uploads, and interactive follow-up questioning.

SKILLS:
- Languages & Core: Python, JavaScript, TypeScript, SQL, C/C++, Java, Go, Bash, HTML/CSS, R
- ML & AI Frameworks: PyTorch, TensorFlow, Keras, Scikit-Learn, XGBoost, LightGBM, Hugging Face Transformers, SpaCy, NLTK, OpenAI API, LangChain, LangGraph, vLLM
- Big Data & Cloud: AWS (EC2, S3, Lambda, SageMaker, Bedrock), GCP, Azure, Apache Spark, Hadoop, Kafka, Snowflake, Databricks, Kubernetes, Docker
- Web & APIs: FastAPI, Flask, Django, React, Node.js, Express.js, REST APIs, GraphQL, WebSocket, Microservices, Nginx

EDUCATION:
- M.S. Data Analytics Engineering, Northeastern University, Boston, USA (GPA: 3.8/4.0) – May 2024
- B.E. Mechanical Engineering, University of Mumbai, India (GPA: 3.7/4.0) – May 2022
"""
