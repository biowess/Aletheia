import asyncio
import os
import sys

# Add the app path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.medical_retrieval_service import MedicalRetrievalService
from app.services.pubmed_client import PubMedClient
from app.reasoning.providers.gemini import GeminiProvider

async def test():
    provider = GeminiProvider(api_key=os.environ.get("GEMINI_API_KEY", "dummy"))
    pubmed_client = PubMedClient(api_key=os.environ.get("NCBI_API_KEY"))
    service = MedicalRetrievalService(provider, pubmed_client)
    text = "The patient presents with severe headaches and hypertension. Guidelines suggest starting ACE inhibitors."
    modified, citations = await service.process_and_inject_citations(text)
    print("Modified:", modified)
    print("Citations:", citations)
    await service.close()

if __name__ == "__main__":
    asyncio.run(test())
