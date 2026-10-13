# My agent: CareerPilot AI
One-liner: A conversational agent that helps job seekers and career switchers analyze resumes, match against target job descriptions, discover skill gaps, build personalized learning roadmaps, and practice role-specific interviews.

Tool coverage:
- Memory: Candidate profile, target roles, target seniority, resume skill inventory, gap analysis history, and interview practice scores across sessions.
- Tools:
  - `parse_resume`: Extracts skills, experience, projects, and education from resume text or sample profiles.
  - `match_job_description`: Analyzes overlap and detects matched skills, missing requirements, and unverified credentials against target JDs.
  - `generate_roadmap`: Generates a milestone-based, step-by-step upskilling roadmap for target role requirements.
  - `generate_interview_questions`: Creates tailored behavioral & technical interview questions based on candidate gaps and job requirements.
  - `evaluate_interview_answer`: Scores candidate responses with rubric-based constructive feedback and suggested model answers.
- Catalog/UI: Catalog of benchmark industry job profiles (e.g., AI/ML Engineer, Cloud Solutions Architect, Full-Stack Developer) and structured skill-gap tables.
- Image gen: Visual career milestone roadmap or practice completion badge.
- Sandbox: Deterministic computation of skill match percentages, weighted gap scores, and interview performance metrics.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code execution for gap percentage calculation, Firestore for storing user profile and interview history, Vertex AI Memory Bank.
