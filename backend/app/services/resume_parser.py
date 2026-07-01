"""
Resume parsing service.

Approach (intentionally rule-based, no external NLP/LLM service, to keep
the project runnable offline within a 3-4 week intern timeline):
  1. Extract all text from the PDF with pdfplumber.
  2. Pull out name/email/phone with regex.
  3. Split the text into rough sections (Education, Experience, Projects,
     Certifications) by scanning for common section headers.
  4. Scan the whole document for any skill in MASTER_SKILLS / its synonyms.

Stretch goal noted in docs/PROJECT_PLAN.md: swap step 4 for an LLM-based
extractor (e.g. via the Anthropic API) for far more accurate, less brittle
parsing once the rule-based version works end-to-end.
"""
import re
from typing import Optional

import pdfplumber

from app.services.skill_data import MASTER_SKILLS, SKILL_SYNONYMS, normalize_skill_list

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[\s-]?)?\(?\d{3,5}\)?[\s-]?\d{3}[\s-]?\d{3,4}")

SECTION_HEADERS = {
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "summary": ["summary", "objective", "professional summary", "profile"],
}


def extract_text_from_pdf(file_path: str) -> str:
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def _extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    match = PHONE_REGEX.search(text)
    return match.group(0).strip() if match else None


def _extract_name(text: str) -> Optional[str]:
    """Heuristic: the first non-empty line that isn't an email/phone/section header is likely the name."""
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) > 60:
            continue
        if EMAIL_REGEX.search(line) or PHONE_REGEX.search(line):
            continue
        lower = line.lower()
        if any(lower.startswith(h) for headers in SECTION_HEADERS.values() for h in headers):
            continue
        return line
    return None


def _split_sections(text: str) -> dict:
    """
    Walk through lines, track which known section we're currently in,
    and bucket lines accordingly. Very lightweight — good enough for
    standard single-column resumes; messier layouts may need manual edits.
    """
    lines = text.splitlines()
    sections = {key: [] for key in SECTION_HEADERS}
    current_section = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower().strip(" :-")

        matched_section = None
        for section_key, headers in SECTION_HEADERS.items():
            if any(lower == h or lower.startswith(h) for h in headers):
                matched_section = section_key
                break

        if matched_section:
            current_section = matched_section
            continue  # the header line itself isn't content

        if current_section:
            sections[current_section].append(line)

    return sections


def _extract_skills(text: str) -> list[str]:
    lower_text = f" {text.lower()} "
    found = []
    for canonical, variants in SKILL_SYNONYMS.items():
        for variant in [canonical] + variants:
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(variant.lower()) + r"(?![a-zA-Z0-9])"
            if re.search(pattern, lower_text):
                found.append(canonical)
                break
    return normalize_skill_list(found)


def parse_resume(file_path: str) -> dict:
    """
    Main entry point. Returns a dict matching the fields stored on ResumeData.
    """
    text = extract_text_from_pdf(file_path)

    sections = _split_sections(text)

    summary_lines = sections.get("summary", [])
    summary = " ".join(summary_lines[:5]) if summary_lines else None

    return {
        "raw_text": text,
        "extracted_name": _extract_name(text),
        "extracted_email": _extract_email(text),
        "extracted_phone": _extract_phone(text),
        "skills": _extract_skills(text),
        "education": sections.get("education", [])[:15],
        "experience": sections.get("experience", [])[:25],
        "projects": sections.get("projects", [])[:15],
        "certifications": sections.get("certifications", [])[:10],
        "summary": summary,
    }
