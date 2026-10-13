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



def _convert_a2ui_to_markdown(data: dict) -> str:
    """Convert an A2UI surfaceUpdate dictionary to clean, readable Markdown text."""
    su = data.get("surfaceUpdate") or data
    components = su.get("components", [])
    lines = []
    for comp in components:
        c = comp.get("component", {})
        txt = c.get("Text")
        if txt:
            val = txt.get("text", {})
            text_str = val.get("literalString", "") if isinstance(val, dict) else str(val)
            hint = txt.get("usageHint", "")
            if hint == "h1":
                lines.append(f"# {text_str}")
            elif hint == "h2":
                lines.append(f"## {text_str}")
            elif hint in ("h3", "h4"):
                lines.append(f"### {text_str}")
            else:
                lines.append(text_str)
        img = c.get("Image")
        if img:
            url_spec = img.get("url", {})
            url = url_spec.get("literalString", "") if isinstance(url_spec, dict) else str(url_spec)
            if url and url.startswith("http"):
                lines.append(f"![Career Visualization]({url})")
    return "\n\n".join([line for line in lines if line.strip()]).strip()


def _clean_and_format_part(raw_text: str) -> str:
    """Detect raw A2UI JSON, JSON arrays, or a2a_datapart envelopes and format cleanly as Markdown."""
    if not raw_text:
        return ""
    raw = raw_text.strip()
    is_a2ui = (
        "<a2a_datapart_json>" in raw
        or "<a2ui-json>" in raw
        or ("surfaceUpdate" in raw and "components" in raw)
        or ("surfaceId" in raw and "components" in raw)
        or (raw.startswith("[") and "components" in raw)
    )
    if is_a2ui:
        import re, json
        # Extract payload inside wrapper tags if present
        m = re.search(r"<(?:a2a_datapart_json|a2ui-json)>(.*?)(?:</(?:a2a_datapart_json|a2ui-json)>|$)", raw, re.DOTALL)
        candidate = m.group(1).strip() if m else raw
        try:
            payload = json.loads(candidate)
            data = payload.get("data", payload) if isinstance(payload, dict) else payload
            if isinstance(data, list):
                res = [_convert_a2ui_to_markdown(item) for item in data if isinstance(item, dict)]
                formatted = "\n\n".join([r for r in res if r])
                if formatted:
                    return formatted
                return ""
            elif isinstance(data, dict):
                # If beginRendering with no components, swallow it so raw envelope is not output
                if "beginRendering" in data and "surfaceUpdate" not in data and "components" not in data:
                    return ""
                formatted = _convert_a2ui_to_markdown(data)
                if formatted:
                    return formatted
                return ""
        except Exception:
            # If partial/malformed JSON, strip any envelope tags
            cleaned = re.sub(r"</?(?:a2a_datapart_json|a2ui-json)>", "", raw).strip()
            return cleaned
    return raw


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Chat with the CareerPilot AI ADK Agent."""
    try:
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
                        cleaned = _clean_and_format_part(part.text)
                        if cleaned:
                            reply_chunks.append(cleaned)
                    elif hasattr(part, "inline_data") and part.inline_data:
                        try:
                            raw = part.inline_data.data.decode("utf-8")
                            cleaned = _clean_and_format_part(raw)
                            if cleaned:
                                reply_chunks.append(cleaned)
                        except Exception:
                            pass

        # Deduplicate consecutive identical chunks if any
        deduped = []
        for chunk in reply_chunks:
            chunk_str = chunk.strip()
            if chunk_str and (not deduped or deduped[-1] != chunk_str):
                deduped.append(chunk_str)

        full_reply = "\n\n".join(deduped).strip()
        if not full_reply:
            full_reply = "CareerPilot successfully executed your request."

        return ChatResponse(reply=full_reply, status="success")
    except Exception as e:
        return ChatResponse(reply=f"Error executing request: {str(e)}", status="error")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8081"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
