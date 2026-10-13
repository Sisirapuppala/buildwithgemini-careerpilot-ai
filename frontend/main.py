"""CareerPilot AI - Web App Backend Server using FastAPI & ADK Agent."""

import os
from dotenv import load_dotenv

# Ensure environment variables from career_pilot/.env are loaded for Vertex AI
env_path = os.path.join(os.path.dirname(__file__), "..", "career_pilot", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import VertexAiMemoryBankService
from career_pilot.agent import root_agent

app = FastAPI(title="CareerPilot AI - Web App")

# Initialize in-memory session service and Vertex AI Memory Bank service
PROJECT_ID = "qwiklabs-gcp-04-6300f100430f"
MEMORY_BANK_ID = "615805951269666816"
session_service = InMemorySessionService()

try:
    memory_service = VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-central1",
        agent_engine_id=MEMORY_BANK_ID,
    )
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Failed to initialize VertexAiMemoryBankService: %s", e)
    memory_service = None

runner = Runner(
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service,
    app_name="career_pilot"
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest_user"
    session_id: str = "default_session"


class ChatResponse(BaseModel):
    reply: str
    status: str = "success"


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    try:
        # Wrap message inside Content
        user_msg = types.Content(
            role="user",
            parts=[types.Part.from_text(text=req.message)]
        )

        # Ensure session exists
        try:
            await session_service.create_session(
                app_name="career_pilot",
                user_id=req.user_id,
                session_id=req.session_id
            )
        except Exception:
            pass

        # Execute query via ADK local runner
        reply_chunks = []
        async for event in runner.run_async(
            user_id=req.user_id,
            session_id=req.session_id,
            new_message=user_msg
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        reply_chunks.append(part.text)
                    elif hasattr(part, "inline_data") and part.inline_data:
                        try:
                            raw = part.inline_data.data.decode("utf-8")
                            import re, json
                            m = re.search(r'<a2a_datapart_json>(.*?)(?:</a2a_datapart_json>|$)', raw)
                            if m:
                                payload = json.loads(m.group(1))
                                # Extract readable text from surfaceUpdate components
                                a2ui_data = payload.get("data", {})
                                su = a2ui_data.get("surfaceUpdate", {})
                                for comp in su.get("components", []):
                                    c_spec = comp.get("component", {})
                                    txt_comp = c_spec.get("Text", {})
                                    if txt_comp:
                                        t_val = txt_comp.get("text", {})
                                        if isinstance(t_val, dict):
                                            reply_chunks.append(t_val.get("literalString", ""))
                                        elif isinstance(t_val, str):
                                            reply_chunks.append(t_val)
                        except Exception:
                            pass

        full_reply = "\n\n".join([c.strip() for c in reply_chunks if c.strip()]).strip()
        if not full_reply:
            full_reply = "CareerPilot successfully executed your request."

        return ChatResponse(reply=full_reply, status="success")
    except Exception as e:
        return ChatResponse(reply=f"Error executing request: {str(e)}", status="error")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8081"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
