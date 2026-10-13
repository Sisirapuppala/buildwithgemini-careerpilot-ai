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

import os
import sys

packages_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
from .a2ui_utils import a2ui_callback

CAREER_ROLE_DESCRIPTION = (
    "CareerPilot AI, an expert agentic Career Assistant powered by Gemini. "
    "You help users navigate their tech career journey: resume parsing, job fit gap analysis, "
    "personalized 6-week roadmaps, interview coaching, and remembering user background, preferences, "
    "and health/personal constraints including remembering all user allergies across sessions."
)

CAREER_WORKFLOW_DESCRIPTION = (
    "Analyze candidate resumes, job descriptions, or user questions. Recall and respect user preferences "
    "and ensure all user allergies (e.g. food allergies at work events, environmental allergies, medical allergies) "
    "stated by the user are explicitly remembered and accommodated in long-term memory. "
    "Return rich, structured UI cards when presenting career analysis, interview feedback, roadmap phases, or milestone badges."
)

CAREER_UI_DESCRIPTION = (
    "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
    "Never nest a Card inside a Card. "
    "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
    "Table or Heading (unsupported), or Buttons, actions, or forms (they do nothing in adk web). "
    "You may include one Image component, but only when you have a public https URL for the image "
    "(for example the URL an image tool returns after uploading to a public bucket). Set the Image url to "
    "that exact https link, for example {\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. "
    "Never point an Image at a bare filename, an artifact name, or a non-http(s) path. If you do not have "
    "a public URL, add a short Text line noting the image instead. "
    "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for headings and emphasis. "
    "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
    "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
)

try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )
    A2UI_INSTRUCTION = schema_manager.generate_system_prompt(
        role_description=CAREER_ROLE_DESCRIPTION,
        workflow_description=CAREER_WORKFLOW_DESCRIPTION,
        ui_description=CAREER_UI_DESCRIPTION,
        include_schema=True,
        include_examples=True,
    )
except Exception:
    import json
    prompt_file = os.path.join(os.path.dirname(__file__), "a2ui_prompt.json")
    if os.path.exists(prompt_file):
        with open(prompt_file) as f:
            A2UI_INSTRUCTION = json.load(f)
    else:
        A2UI_INSTRUCTION = (
            f"{CAREER_ROLE_DESCRIPTION}\n\n{CAREER_WORKFLOW_DESCRIPTION}\n\n{CAREER_UI_DESCRIPTION}"
        )

# WRITE: after each turn, send the session to Memory Bank for durable fact extraction
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None

# Agent Engine instance from deployment_metadata.json
AGENT_ENGINE_RESOURCE = "projects/580283762535/locations/us-central1/reasoningEngines/615805951269666816"

root_agent = Agent(
    model='gemini-3.8-flash',
    name='career_pilot_agent',
    description='CareerPilot AI: Intelligent resume parser, job fit analyzer, roadmap builder, and interview coach with A2UI, Memory Bank, Sandbox, Firestore, and Maps.',
    instruction=A2UI_INSTRUCTION,
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
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)
