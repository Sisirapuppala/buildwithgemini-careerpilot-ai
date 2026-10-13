"""Deterministic and structured tools for CareerPilot AI."""

from typing import Any
import re
import json
from career_pilot.sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS


def list_sample_profiles() -> dict[str, Any]:
    """Lists the available pre-loaded benchmark resumes and job descriptions.
    
    Use this tool when a user asks to see sample profiles or test cases without pasting their own.
    """
    return {
        "sample_resumes": list(SAMPLE_RESUMES.keys()),
        "sample_job_descriptions": list(SAMPLE_JOB_DESCRIPTIONS.keys())
    }


def load_sample_resume(resume_key: str) -> str:
    """Loads text for a sample resume by key name.
    
    Args:
        resume_key: One of 'junior_software_engineer', 'data_analyst_switcher', or 'incomplete_malformed_resume'.
    """
    return SAMPLE_RESUMES.get(resume_key, f"Error: Sample resume '{resume_key}' not found. Available: {list(SAMPLE_RESUMES.keys())}")


def load_sample_job_description(job_key: str) -> str:
    """Loads text for a sample job description by key name.
    
    Args:
        job_key: One of 'ai_ml_engineer', 'fullstack_cloud_developer', or 'nurse_practitioner_mismatched'.
    """
    return SAMPLE_JOB_DESCRIPTIONS.get(job_key, f"Error: Sample job description '{job_key}' not found. Available: {list(SAMPLE_JOB_DESCRIPTIONS.keys())}")


def parse_resume_content(resume_text: str) -> dict[str, Any]:
    """Parses and extracts structured sections (skills, experience summary, education) from resume text.
    
    Args:
        resume_text: Raw resume text.
        
    Returns:
        Structured breakdown of extracted technical skills, tools, and experience indicators.
    """
    if not resume_text or len(resume_text.strip()) < 20:
        return {
            "status": "incomplete_or_invalid",
            "message": "Resume text is too brief or malformed to extract sufficient career information.",
            "extracted_skills": [],
            "extracted_tools": [],
            "experience_years_estimate": 0,
            "detected_sections": []
        }

    text_lower = resume_text.lower()
    common_skills = [
        "python", "javascript", "typescript", "java", "c++", "go", "sql", "r", "html", "css",
        "flask", "fastapi", "react", "django", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "docker", "kubernetes", "git", "github", "postgres", "postgresql", "sqlite", "mongodb", "firestore",
        "gcp", "google cloud", "vertex ai", "cloud run", "cloud storage", "rag", "llm", "rest api", "unit testing", "pytest"
    ]

    found_skills = [skill for skill in common_skills if re.search(rf"\b{re.escape(skill)}\b", text_lower)]
    
    # Estimate years of experience
    exp_matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)\b", text_lower)
    exp_years = float(exp_matches[0]) if exp_matches else (1.0 if "junior" in text_lower else 2.0)

    sections = []
    for section_name in ["skills", "experience", "education", "projects", "summary"]:
        if section_name in text_lower:
            sections.append(section_name.title())

    return {
        "status": "success",
        "extracted_skills": sorted(list(set(found_skills))),
        "experience_years_estimate": exp_years,
        "detected_sections": sections,
        "raw_character_count": len(resume_text)
    }


def compare_resume_with_job(resume_text: str, job_description_text: str) -> dict[str, Any]:
    """Compares candidate resume text against a target job description to compute matched and missing skills.
    
    Args:
        resume_text: The candidate's resume content.
        job_description_text: The target job description text.
        
    Returns:
        Detailed match breakdown, percentage score, matched skills, missing requirements, and recommendations.
    """
    parsed_resume = parse_resume_content(resume_text)
    if parsed_resume.get("status") == "incomplete_or_invalid":
        return {
            "status": "error",
            "message": "Cannot evaluate job match because resume content is incomplete or malformed.",
            "match_score_percentage": 0.0,
            "matched_skills": [],
            "missing_skills": ["Sufficient resume details needed"]
        }

    jd_lower = job_description_text.lower()
    
    # Known benchmark requirements
    potential_job_skills = [
        "python", "javascript", "typescript", "fastapi", "flask", "react", "sql", "postgresql", "firestore",
        "docker", "kubernetes", "cloud run", "vertex ai", "google cloud", "rag", "llm", "pytest", "unit testing",
        "rest api", "ci/cd", "a2ui", "prompt engineering", "git", "acute care", "nurse", "bls", "acls", "iv therapy"
    ]

    jd_required_skills = [
        skill for skill in potential_job_skills if re.search(rf"\b{re.escape(skill)}\b", jd_lower)
    ]

    if not jd_required_skills:
        # Fallback keyword extraction
        words = re.findall(r"\b[a-zA-Z]{3,15}\b", jd_lower)
        jd_required_skills = list(set([w for w in words if w in potential_job_skills]))

    resume_skills_set = set(parsed_resume.get("extracted_skills", []))
    
    matched = [s for s in jd_required_skills if s in resume_skills_set]
    missing = [s for s in jd_required_skills if s not in resume_skills_set]

    total_reqs = len(jd_required_skills)
    score = (len(matched) / total_reqs * 100.0) if total_reqs > 0 else 0.0

    return {
        "status": "success",
        "match_score_percentage": round(score, 1),
        "total_job_requirements_detected": total_reqs,
        "matched_skills": matched,
        "missing_skills": missing,
        "unverified_credentials": [
            "Official cloud certifications" if "certified" in jd_lower else None,
            "Production multi-agent deployment track record" if "a2ui" in jd_lower or "orchestration" in jd_lower else None
        ],
        "is_career_pivot": len(matched) < 2 and total_reqs > 3
    }


def generate_learning_roadmap(target_role: str, missing_skills: list[str], timeline_weeks: int = 6) -> dict[str, Any]:
    """Generates a structured, week-by-week learning roadmap for missing skills.
    
    Args:
        target_role: The desired career role (e.g. 'AI/ML Solutions Engineer').
        missing_skills: List of skills to acquire.
        timeline_weeks: Desired timeline in weeks (default: 6).
        
    Returns:
        Structured roadmap milestones, focus areas, and recommended practical project.
    """
    if not missing_skills:
        return {
            "target_role": target_role,
            "message": "Candidate already possesses core skills! Focus on portfolio refinement and mock interview practice.",
            "milestones": []
        }

    weeks_per_skill = max(1, timeline_weeks // max(1, len(missing_skills)))
    milestones = []
    current_week = 1

    for idx, skill in enumerate(missing_skills[:6]):
        end_week = min(timeline_weeks, current_week + weeks_per_skill - 1)
        milestones.append({
            "phase": f"Phase {idx + 1} (Weeks {current_week}-{end_week})",
            "skill": skill.capitalize(),
            "objective": f"Master fundamentals of {skill} and complete 1 hands-on exercise.",
            "deliverable": f"Deploy a small component or test harness using {skill}."
        })
        current_week = end_week + 1
        if current_week > timeline_weeks:
            break

    return {
        "target_role": target_role,
        "total_weeks": timeline_weeks,
        "milestones": milestones,
        "capstone_recommendation": f"Build an end-to-end {target_role} showcase project integrating {', '.join(missing_skills[:3])}."
    }


def evaluate_interview_response(question: str, candidate_answer: str, target_role: str = "General") -> dict[str, Any]:
    """Evaluates a candidate's answer to a mock interview question.
    
    Args:
        question: The interview question asked.
        candidate_answer: The user's response.
        target_role: The role context (e.g., 'AI/ML Engineer').
        
    Returns:
        Quantitative rubric scores (1-10) for Clarity, Technical Depth, and STAR alignment, plus specific feedback.
    """
    answer_clean = candidate_answer.strip()
    words = answer_clean.split()
    word_count = len(words)

    if word_count < 10:
        return {
            "score_out_of_10": 3.0,
            "clarity_score": 4.0,
            "depth_score": 2.0,
            "feedback": "Answer is too brief. Elaborate using the STAR method (Situation, Task, Action, Result) with specific tools and outcomes.",
            "strengths": ["Direct response"],
            "areas_for_improvement": ["Add concrete examples, metrics, and details of technical challenges overcome."]
        }

    # Keyword depth check
    keywords = ["because", "result", "improved", "architecture", "scale", "tested", "deployed", "pipeline", "handled", "metrics"]
    found_keywords = [k for k in keywords if k in answer_clean.lower()]

    clarity = min(10.0, 6.0 + (word_count // 30))
    depth = min(10.0, 5.0 + len(found_keywords) * 0.8)
    overall = round((clarity * 0.4 + depth * 0.6), 1)

    return {
        "score_out_of_10": overall,
        "clarity_score": clarity,
        "technical_depth_score": depth,
        "feedback": f"Strong structured attempt for a {target_role} position. Demonstrated knowledge of key technical principles.",
        "strengths": [f"Demonstrated technical context with keywords ({', '.join(found_keywords[:3])})" if found_keywords else "Clear communication"],
        "areas_for_improvement": ["Quantify business or latency impact (e.g., 'reduced inference time by 25%')", "Mention edge cases or monitoring strategies."]
    }


# In-memory candidate profile store for local session persistence
_ACTIVE_USER_PROFILE = {
    "target_role": "AI/ML Solutions Engineer",
    "saved_skills": ["Python", "Flask", "PostgreSQL", "Docker", "RESTful APIs"],
    "target_seniority": "Mid-Level",
    "identified_gaps": ["Vertex AI", "Cloud Run", "RAG", "LLMs"],
    "completed_practice_questions": [
        {
            "question": "Can you walk through how you design an end-to-end RAG pipeline?",
            "score": 5.8,
            "key_takeaway": "Focus on hybrid search, reranking layer, and faithfulness evaluation."
        }
    ]
}


def get_candidate_profile() -> dict[str, Any]:
    """Retrieves the candidate's current persistent career profile, target role, saved skills, and practice history.
    
    Use this tool whenever the user asks 'What do you remember about me?', 'What are my goals?', or wants personalized context.
    """
    return {
        "status": "success",
        "profile": _ACTIVE_USER_PROFILE
    }


def update_candidate_profile(target_role: str = None, target_seniority: str = None, additional_skills: list[str] = None) -> dict[str, Any]:
    """Updates candidate preferences, target role, seniority, or acquired skills in their persistent profile.
    
    Args:
        target_role: New target job title (e.g., 'Cloud AI Engineer').
        target_seniority: New target level (e.g., 'Senior', 'Lead').
        additional_skills: New skills acquired or validated.
    """
    if target_role:
        _ACTIVE_USER_PROFILE["target_role"] = target_role
    if target_seniority:
        _ACTIVE_USER_PROFILE["target_seniority"] = target_seniority
    if additional_skills:
        for s in additional_skills:
            if s not in _ACTIVE_USER_PROFILE["saved_skills"]:
                _ACTIVE_USER_PROFILE["saved_skills"].append(s)
                
    return {
        "status": "success",
        "message": "Candidate career profile successfully updated.",
        "updated_profile": _ACTIVE_USER_PROFILE
    }
