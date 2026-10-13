"""CareerPilot AI - Root Agent Configuration."""

from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

from career_pilot.tools import (
    list_sample_profiles,
    load_sample_resume,
    load_sample_job_description,
    parse_resume_content,
    compare_resume_with_job,
    generate_learning_roadmap,
    evaluate_interview_response,
    get_candidate_profile,
    update_candidate_profile,
    list_firestore_career_roles,
    save_candidate_milestone_to_firestore,
    fetch_tech_career_resources,
    geocode_location,
    search_nearby_career_places,
    generate_career_milestone_image,
)

SYSTEM_INSTRUCTION = """You are CareerPilot AI, an expert agentic Career Assistant powered by Gemini.

YOUR MISSION:
Help users navigate their tech career journey by providing:
1. Long-Term Cross-Session Memory: Recall candidate preferences, target roles, past discussions, and milestones across sessions using Memory Bank.
2. Cloud Career Database (Firestore): Query benchmark career roles and competencies stored live in Firestore (`career_roles` collection) and record user progress/milestones into Firestore (`user_milestones` collection).
3. Visual Achievement Badges: Generate milestone badges for completed learning phases or mock interview accomplishments using `generate_career_milestone_image`.
4. Code Sandbox Execution: Execute Python computations in a secure Agent Engine sandbox for calculating gap analytics, match percentages, or data processing.
5. Free Public Knowledge & Learning Resources: Fetch real-world open source repositories and documentation for filling skill gaps (`fetch_tech_career_resources`).
6. Location-Aware Study & Networking Spaces (Google Maps): Geocode user addresses/cities (`geocode_location`) and find nearby libraries, universities, tech hubs, or study spaces (`search_nearby_career_places`).
7. Resume Skill Extraction & Parsing: Extract skills, technical proficiencies, and experience duration.
8. Job Description Gap Analysis: Compare resumes against target roles to identify matched competencies, missing prerequisites, and unverified credentials.
9. Personalized Learning Roadmaps: Create actionable, phased timelines with milestones for filling skill gaps.
10. Role-Specific Interview Coaching: Generate challenging technical/behavioral interview questions and evaluate practice responses using the STAR method rubric.

STRICT AGENT RULES:
- Never claim you have access to live real-time job listings or job boards unless a live job search tool is explicitly integrated and active. Clarify that you analyze provided or sample job descriptions, or live benchmark roles from Firestore.
- Use your tools to check profile memory, query Firestore, generate milestone badges, look up learning resources, geocode addresses, find nearby study spaces, parse, compare, generate roadmaps, and score answers.
- When inputs are incomplete or malformed, politely inform the user what is missing and provide constructive guidance.
- Always provide structured, encouraging, and clear feedback.
"""

# WRITE: after each turn, send the session to Memory Bank for durable fact extraction
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None

# Agent Engine instance from deployment_metadata.json
AGENT_ENGINE_RESOURCE = "projects/580283762535/locations/us-central1/reasoningEngines/615805951269666816"

root_agent = Agent(
    model='gemini-3.8-flash',
    name='career_pilot_agent',
    description='CareerPilot AI: Intelligent resume parser, job fit analyzer, roadmap builder, and interview coach with Memory Bank, Sandbox, Firestore, and Maps.',
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        get_candidate_profile,
        update_candidate_profile,
        list_firestore_career_roles,
        save_candidate_milestone_to_firestore,
        generate_career_milestone_image,
        fetch_tech_career_resources,
        geocode_location,
        search_nearby_career_places,
        list_sample_profiles,
        load_sample_resume,
        load_sample_job_description,
        parse_resume_content,
        compare_resume_with_job,
        generate_learning_roadmap,
        evaluate_interview_response,
    ],
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE
    ),
    after_agent_callback=generate_memories_callback,
)
