"""Test suite for CareerPilot AI tools and agent behaviors."""

import unittest
from career_pilot.sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS
from career_pilot.tools import (
    parse_resume_content,
    compare_resume_with_job,
    generate_learning_roadmap,
    evaluate_interview_response,
    list_sample_profiles,
    load_sample_resume,
    load_sample_job_description,
)


class TestCareerPilot(unittest.TestCase):

    def test_list_and_load_sample_profiles(self):
        """Verify sample fixtures load properly."""
        profiles = list_sample_profiles()
        self.assertIn("junior_software_engineer", profiles["sample_resumes"])
        self.assertIn("ai_ml_engineer", profiles["sample_job_descriptions"])

        resume = load_sample_resume("junior_software_engineer")
        self.assertIn("John Doe", resume)

        jd = load_sample_job_description("ai_ml_engineer")
        self.assertIn("AI/ML Solutions Engineer", jd)

    def test_parse_normal_resume(self):
        """Verify parsing normal detailed resume."""
        resume_text = SAMPLE_RESUMES["junior_software_engineer"]
        parsed = parse_resume_content(resume_text)

        self.assertEqual(parsed["status"], "success")
        self.assertIn("python", parsed["extracted_skills"])
        self.assertIn("flask", parsed["extracted_skills"])
        self.assertIn("react", parsed["extracted_skills"])
        self.assertIn("pytest", parsed["extracted_skills"])
        self.assertGreaterEqual(parsed["experience_years_estimate"], 1.0)

    def test_parse_incomplete_malformed_resume(self):
        """Verify graceful degradation when given an incomplete resume."""
        malformed_text = SAMPLE_RESUMES["incomplete_malformed_resume"]
        parsed = parse_resume_content(malformed_text)

        self.assertIn("status", parsed)
        self.assertIsInstance(parsed["extracted_skills"], list)

    def test_compare_resume_with_matching_job(self):
        """Verify matching skills and gap detection."""
        resume_text = SAMPLE_RESUMES["junior_software_engineer"]
        jd_text = SAMPLE_JOB_DESCRIPTIONS["ai_ml_engineer"]

        comparison = compare_resume_with_job(resume_text, jd_text)
        self.assertEqual(comparison["status"], "success")
        self.assertIn("python", comparison["matched_skills"])
        self.assertTrue(any(skill in comparison["missing_skills"] for skill in ["vertex ai", "cloud run", "rag", "llm"]))
        self.assertGreater(comparison["match_score_percentage"], 0)

    def test_compare_mismatched_job(self):
        """Verify mismatch detection for completely unrelated jobs."""
        resume_text = SAMPLE_RESUMES["junior_software_engineer"]
        mismatched_jd = SAMPLE_JOB_DESCRIPTIONS["nurse_practitioner_mismatched"]

        comparison = compare_resume_with_job(resume_text, mismatched_jd)
        self.assertEqual(comparison["status"], "success")
        self.assertEqual(comparison["match_score_percentage"], 0.0)

    def test_generate_learning_roadmap(self):
        """Verify roadmap phase generation."""
        missing = ["vertex ai", "cloud run", "rag", "docker"]
        roadmap = generate_learning_roadmap("AI/ML Engineer", missing, timeline_weeks=8)

        self.assertEqual(roadmap["target_role"], "AI/ML Engineer")
        self.assertGreater(len(roadmap["milestones"]), 0)
        self.assertIn("capstone_recommendation", roadmap)

    def test_evaluate_interview_response_short(self):
        """Verify evaluation detects too-short answer."""
        eval_result = evaluate_interview_response(
            question="Tell me about a time you resolved an outage.",
            candidate_answer="I restarted the server.",
            target_role="Cloud Engineer"
        )
        self.assertLessEqual(eval_result["score_out_of_10"], 5.0)
        self.assertIn("STAR", eval_result["feedback"])

    def test_evaluate_interview_response_detailed(self):
        """Verify evaluation rewards detailed technical answer."""
        eval_result = evaluate_interview_response(
            question="How do you deploy LLMs reliably in production?",
            candidate_answer="In my past project, we deployed an agent pipeline to Cloud Run and Vertex AI. Because we handled streaming responses with SSE, we improved user latency. We also tested all tools thoroughly using unit testing to scale reliably.",
            target_role="AI Solutions Engineer"
        )
        self.assertGreaterEqual(eval_result["score_out_of_10"], 6.5)
        self.assertGreater(len(eval_result["strengths"]), 0)


    def test_candidate_profile_memory_tools(self):
        """Verify candidate profile memory retrieval and update."""
        from career_pilot.tools import get_candidate_profile, update_candidate_profile
        
        prof = get_candidate_profile()
        self.assertEqual(prof["status"], "success")
        self.assertIn("target_role", prof["profile"])
        
        upd = update_candidate_profile(target_role="Lead AI Architect", additional_skills=["Kubernetes"])
        self.assertEqual(upd["status"], "success")
        self.assertEqual(upd["updated_profile"]["target_role"], "Lead AI Architect")
        self.assertIn("Kubernetes", upd["updated_profile"]["saved_skills"])


    def test_firestore_tools(self):
        """Verify Firestore read and write tools."""
        from career_pilot.tools import list_firestore_career_roles, save_candidate_milestone_to_firestore

        roles_res = list_firestore_career_roles()
        self.assertEqual(roles_res["status"], "success")
        self.assertGreater(len(roles_res["roles"]), 0)

        save_res = save_candidate_milestone_to_firestore(
            user_id="test_candidate_unit",
            milestone_title="Mastered Vector Indexing",
            target_role="AI/ML Solutions Engineer",
            details="Scored 9/10 in mock test."
        )
        self.assertEqual(save_res["status"], "success")
        self.assertIn("document_id", save_res)


    def test_fetch_tech_career_resources(self):
        """Verify public API tech resource lookup."""
        from career_pilot.tools import fetch_tech_career_resources
        res = fetch_tech_career_resources("python")
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["top_resources"]), 0)


    def test_maps_tools_graceful_missing_key(self):
        """Verify Maps tools gracefully inform user if GOOGLE_MAPS_API_KEY is not set."""
        from career_pilot.tools import geocode_location, search_nearby_career_places
        
        geo_res = geocode_location("New York")
        self.assertEqual(geo_res["status"], "error")
        self.assertIn("GOOGLE_MAPS_API_KEY", geo_res["message"])

        places_res = search_nearby_career_places(40.7128, -74.0060, "library")
        self.assertEqual(places_res["status"], "error")
        self.assertIn("GOOGLE_MAPS_API_KEY", places_res["message"])


if __name__ == "__main__":
    unittest.main()
