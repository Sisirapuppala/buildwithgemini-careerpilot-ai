"""Seed Firestore with benchmark career profiles and target job catalog."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-6300f100430f"

SEED_CAREER_PATHS = [
    {
        "id": "ai_ml_engineer",
        "role_title": "AI/ML Solutions Engineer",
        "category": "Artificial Intelligence",
        "required_skills": ["Python", "Vertex AI", "RAG", "LLMs", "Docker", "FastAPI", "Vector Search"],
        "recommended_seniority": "Mid-to-Senior",
        "roadmap_duration_weeks": 6,
        "sample_interview_topics": [
            "End-to-end RAG architecture & vector indexing",
            "Evaluating LLM faithfulness & groundness",
            "Latency vs precision tradeoffs in rerankers"
        ]
    },
    {
        "id": "cloud_solutions_architect",
        "role_title": "Google Cloud Solutions Architect",
        "category": "Cloud Infrastructure",
        "required_skills": ["GCP", "Cloud Run", "Terraform", "Kubernetes", "IAM", "Networking", "Microservices"],
        "recommended_seniority": "Senior",
        "roadmap_duration_weeks": 8,
        "sample_interview_topics": [
            "Designing multi-region resilient architectures",
            "Principle of least privilege in IAM & service accounts",
            "Migrating monolithic apps to Cloud Run / GKE"
        ]
    },
    {
        "id": "fullstack_cloud_developer",
        "role_title": "Fullstack Cloud Developer",
        "category": "Software Engineering",
        "required_skills": ["Python", "TypeScript", "React", "FastAPI", "PostgreSQL", "Docker", "CI/CD"],
        "recommended_seniority": "Junior-to-Mid",
        "roadmap_duration_weeks": 6,
        "sample_interview_topics": [
            "RESTful API design and status code contracts",
            "State management and asynchronous data fetching in React",
            "Containerizing web applications and setting up CI/CD"
        ]
    }
]

def seed_database():
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("career_roles")

    for item in SEED_CAREER_PATHS:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"✓ Seeded career role: {doc_id} -> '{item['role_title']}'")

    print("\nFirestore successfully seeded with benchmark career roles!")

if __name__ == "__main__":
    seed_database()
