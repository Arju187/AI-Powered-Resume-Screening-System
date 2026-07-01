"""
Recommendation engine: the cross-matching logic from the spec.

Given a candidate's normalized skill set and a job's required skills, this
computes a weighted overlap score (a transparent, explainable alternative
to semantic/embedding similarity — appropriate for the rule-based scope of
this build). The same compute_match() function powers both directions:

  - recommend_jobs_for_candidate(): "show this candidate every job they're
    a reasonable fit for, not just the one they searched for"
  - rank_candidates_for_job(): admin's ranked candidate list per job posting

Score weighting:
  Skill overlap   70%
  Experience fit  30%   (candidate meets/exceeds required experience)
"""
from app.services.skill_data import normalize_skill_list


def compute_match(candidate_skills: list[str], job_skills: list[str],
                   candidate_years: float, required_years: float) -> dict:
    cand_norm = set(normalize_skill_list(candidate_skills))
    job_norm = set(normalize_skill_list(job_skills))

    if not job_norm:
        skill_score = 0.0
        matched, missing = [], []
    else:
        matched = sorted(cand_norm & job_norm)
        missing = sorted(job_norm - cand_norm)
        skill_score = (len(matched) / len(job_norm)) * 100

    if required_years and required_years > 0:
        experience_score = min(100.0, (candidate_years / required_years) * 100)
    else:
        experience_score = 100.0  # no experience requirement specified

    final_score = round((skill_score * 0.70) + (experience_score * 0.30), 1)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": sorted(cand_norm - job_norm),
        "skill_score": round(skill_score, 1),
        "experience_score": round(experience_score, 1),
        "recommendation_score": final_score,
    }


def recommend_jobs_for_candidate(candidate_skills: list[str], candidate_years: float,
                                  jobs: list, min_score: float = 25.0, limit: int = 10) -> list[dict]:
    """
    jobs: list of Job ORM instances (only 'open' jobs should be passed in).
    Returns jobs sorted by recommendation_score desc, each annotated with the match info.
    This is what lets a candidate who applied to "Java Developer" but has
    React/Node skills too automatically surface in Java AND React AND
    Node job recommendation lists.
    """
    results = []
    for job in jobs:
        match = compute_match(candidate_skills, job.required_skills or [],
                               candidate_years, job.required_experience or 0)
        if match["recommendation_score"] >= min_score:
            results.append({"job": job, **match})
    results.sort(key=lambda r: r["recommendation_score"], reverse=True)
    return results[:limit]


def rank_candidates_for_job(job_required_skills: list[str], job_required_years: float,
                             applications: list) -> list[dict]:
    """
    applications: list of Application ORM instances (joined to their candidate),
    already filtered to a single job.
    Returns the same applications annotated + sorted by recommendation_score desc —
    this powers the admin "Top Matching Candidates" view per job.
    """
    results = []
    for app in applications:
        candidate = app.candidate
        skills = list(candidate.technical_skills or [])
        if candidate.resume_data and candidate.resume_data.skills:
            skills += [s for s in candidate.resume_data.skills if s not in skills]

        match = compute_match(skills, job_required_skills, candidate.years_experience or 0, job_required_years)
        results.append({"application": app, "candidate": candidate, **match})

    results.sort(key=lambda r: r["recommendation_score"], reverse=True)
    return results
