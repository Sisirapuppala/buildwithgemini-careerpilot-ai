"""CareerPilot AI Package."""

# Memory service configuration for deployment
from google.adk.memory import VertexAiMemoryBankService

def memory_bank_service_builder():
    """Builds the Vertex AI Memory Bank service reusing the deployed Agent Engine."""
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-04-6300f100430f",
        location="us-central1",
        agent_engine_id="615805951269666816",
    )
