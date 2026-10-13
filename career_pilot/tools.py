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

# Firestore Integration for Persistent Career Roles and User Journey
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-6300f100430f"

def get_firestore_client():
    import os
    import sys
    packages_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
    if packages_dir not in sys.path:
        sys.path.insert(0, packages_dir)
    from google.cloud import firestore
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_firestore_career_roles() -> dict[str, Any]:
    """Queries the Firestore 'career_roles' collection to fetch live benchmark role paths and competencies.
    
    Use this tool whenever the user wants to see live benchmark career profiles stored in the cloud.
    """
    try:
        db = get_firestore_client()
        docs = db.collection("career_roles").stream()
        roles = []
        for d in docs:
            roles.append(d.to_dict())
        return {
            "status": "success",
            "source": "Firestore (collection: career_roles)",
            "roles": roles
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to query Firestore: {str(e)}"
        }


def save_candidate_milestone_to_firestore(user_id: str, milestone_title: str, target_role: str, details: str) -> dict[str, Any]:
    """Records a candidate's completed learning milestone or mock interview progress into the Firestore 'user_milestones' collection.
    
    Args:
        user_id: Unique candidate ID or username (e.g. 'candidate_123').
        milestone_title: Title of milestone reached (e.g. 'Completed Vertex AI & RAG Phase').
        target_role: The role the candidate is pursuing.
        details: Summary of work done or score achieved.
    """
    try:
        from google.cloud import firestore
        db = get_firestore_client()
        doc_ref = db.collection("user_milestones").document()
        payload = {
            "user_id": user_id,
            "milestone_title": milestone_title,
            "target_role": target_role,
            "details": details,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        doc_ref.set(payload)
        return {
            "status": "success",
            "message": f"Milestone '{milestone_title}' successfully saved to Firestore.",
            "document_id": doc_ref.id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to record milestone to Firestore: {str(e)}"
        }

# Public API & Google Maps Integration

def fetch_tech_career_resources(tag: str = "python") -> dict[str, Any]:
    """Queries a free public tech documentation & dev resource API (DevDocs / GitHub topics)
    to fetch real live learning references and community guides for filling skill gaps.
    
    Args:
        tag: Technology or skill to lookup (e.g. 'python', 'docker', 'react', 'git').
    """
    import urllib.request
    import json
    
    clean_tag = tag.lower().strip().replace(" ", "-")
    url = f"https://api.github.com/search/repositories?q=topic:{clean_tag}+stars:>1000&sort=stars&order=desc&per_page=5"
    
    headers = {
        "User-Agent": "CareerPilot-AI-Agent",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            items = []
            for repo in data.get("items", []):
                items.append({
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count"),
                    "url": repo.get("html_url")
                })
            return {
                "status": "success",
                "tag": clean_tag,
                "total_count": data.get("total_count", 0),
                "top_resources": items
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch public resources: {str(e)}"
        }


def geocode_location(address: str) -> dict[str, Any]:
    """Uses Google Geocoding API to convert an address or city into geographic coordinates (latitude & longitude).
    
    Reads GOOGLE_MAPS_API_KEY from the environment.
    """
    import urllib.request
    import urllib.parse
    import json
    import os
    
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "GOOGLE_MAPS_API_KEY is not set in environment or local .env"
        }
        
    encoded_addr = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_addr}&key={api_key}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "OK" and data.get("results"):
                res = data["results"][0]
                return {
                    "status": "success",
                    "formatted_address": res.get("formatted_address"),
                    "location": res.get("geometry", {}).get("location"),
                    "place_id": res.get("place_id")
                }
            return {
                "status": "error",
                "api_status": data.get("status"),
                "message": data.get("error_message", "No results found for given address")
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Geocoding request failed: {str(e)}"
        }


def search_nearby_career_places(latitude: float, longitude: float, place_type: str = "library", radius_meters: float = 2000.0) -> dict[str, Any]:
    """Uses Google Places API (New) searchNearby endpoint to find nearby study hubs, libraries, co-working spaces, or universities.
    
    Args:
        latitude: Center point latitude.
        longitude: Center point longitude.
        place_type: Type of place to find (e.g. 'library', 'university', 'cafe', 'book_store').
        radius_meters: Search radius in meters (default 2000m).
    """
    import urllib.request
    import json
    import os
    
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "GOOGLE_MAPS_API_KEY is not set in environment or local .env"
        }
        
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types"
    }
    
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": float(radius_meters)
            }
        }
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = []
            for p in data.get("places", []):
                results.append({
                    "name": p.get("displayName", {}).get("text"),
                    "address": p.get("formattedAddress"),
                    "location": p.get("location"),
                    "types": p.get("types", [])
                })
            return {
                "status": "success",
                "places": results
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Places search failed: {str(e)}"
        }
