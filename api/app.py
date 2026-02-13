import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.orchestrator import handle_customer_query

app = FastAPI(
    title="AI Customer Support Agent",
    description="Multi-agent customer support system using RAG, AutoGen, and MCP",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "What is your refund policy?"},
                {"message": "Where is my order #1234?"},
            ]
        }
    }


class ChatResponse(BaseModel):
    reply: str
    status: str = "success"


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Customer Support Agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = await handle_customer_query(request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
