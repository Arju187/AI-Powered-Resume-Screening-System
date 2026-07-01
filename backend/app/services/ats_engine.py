"""
ATS (Applicant Tracking System) scoring engine.

Mirrors the weighting scheme from the original spec, scaled to what we can
realistically compute without a job-specific target (the score here is a
*general resume strength score* computed at upload/profile-update time):

    Skill richness        50%
    Experience             20%
    Education              10%
    Projects                10%
    Certifications           5%
    Resume completeness      5%

When a candidate applies to a *specific* job, a separate, job-aware
recommendation_score is computed by recommendation_engine.py — that one
is what actually drives ranking on a job's candidate list.
"""

# A reasonably "complete" resume might list this many distinct skills.
SKILL_RICHNESS_TARGET = 12
EXPERIENCE_TARGET_YEARS = 8


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def calculate_ats_score(candidate_profile, resume_data) -> tuple[float, dict]:
    """
    candidate_profile: CandidateProfile ORM instance (or any object with the
                        same attributes: years_experience, expected_salary, etc.)
    resume_data: ResumeData ORM instance, or None if no resume uploaded yet.

    Returns (final_score: float 0-100, breakdown: dict)
    """
    skills = list(resume_data.skills) if resume_data and resume_data.skills else []
    education = list(resume_data.education) if resume_data and resume_data.education else []
    experience_lines = list(resume_data.experience) if resume_data and resume_data.experience else []
    projects = list(resume_data.projects) if resume_data and resume_data.projects else []
    certifications = list(resume_data.certifications) if resume_data and resume_data.certifications else []

    # Merge in any manually-entered technical skills on the profile
    if candidate_profile.technical_skills:
        for s in candidate_profile.technical_skills:
            if s not in skills:
                skills.append(s)

    skill_match = _clamp((len(skills) / SKILL_RICHNESS_TARGET) * 100)

    years = candidate_profile.years_experience or 0
    experience_match = _clamp((years / EXPERIENCE_TARGET_YEARS) * 100)

    education_match = 100 if (education or candidate_profile.highest_qualification) else 0
    projects_match = _clamp((len(projects) / 3) * 100)
    certifications_match = _clamp((len(certifications) / 2) * 100)

    # Completeness: how many of the "important" resume sections are present
    filled_sections = sum([
        bool(skills),
        bool(education or candidate_profile.highest_qualification),
        bool(experience_lines or years > 0),
        bool(projects),
        bool(resume_data and resume_data.raw_text),
    ])
    completeness = (filled_sections / 5) * 100

    final_score = (
        skill_match * 0.50
        + experience_match * 0.20
        + education_match * 0.10
        + projects_match * 0.10
        + certifications_match * 0.05
        + completeness * 0.05
    )

    breakdown = {
        "skill_match": round(skill_match, 1),
        "experience_match": round(experience_match, 1),
        "education_match": round(education_match, 1),
        "projects_match": round(projects_match, 1),
        "certifications_match": round(certifications_match, 1),
        "completeness": round(completeness, 1),
        "weights": {
            "skill_match": "50%", "experience_match": "20%", "education_match": "10%",
            "projects_match": "10%", "certifications_match": "5%", "completeness": "5%",
        },
    }

    return round(_clamp(final_score), 1), breakdown


def calculate_profile_completion(candidate_profile, resume_data) -> float:
    """Separate, simpler metric: % of profile fields filled in (drives the dashboard progress bar)."""
    fields = [
        candidate_profile.current_company,
        candidate_profile.current_designation,
        candidate_profile.highest_qualification,
        candidate_profile.location,
        candidate_profile.preferred_job_role,
        candidate_profile.linkedin_url,
        candidate_profile.github_url,
        bool(candidate_profile.technical_skills),
        candidate_profile.resume_path,
        resume_data is not None,
    ]
    filled = sum(1 for f in fields if f)
    return round((filled / len(fields)) * 100, 1)
