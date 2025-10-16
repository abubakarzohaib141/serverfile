# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ChatRequest, ChatResponse, Message
from app.chatbot import run_agent  # your real Gemini chatbot
from app.settings import settings

# Initialize FastAPI
app = FastAPI(title="ABZ Agent API", version="0.1.0")

# CORS settings (for your Next.js frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.CORS_ALLOW_ORIGINS[0] if hasattr(settings, "CORS_ALLOW_ORIGINS") else "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/health")
def health():
    return {"ok": True, "name": "ABZ Agent API", "status": "running"}

# Main chat route (calls Gemini via abagentsdk)
@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    ABZ Chatbot endpoint.
    Calls your Gemini-powered agent using abagentsdk.
    """
    try:
        messages = [m.model_dump() for m in req.messages]
        answer = await run_agent(messages)
        return ChatResponse(message=Message(role="assistant", content=answer))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {e}")

# Optional redirect for convenience
@app.get("/", include_in_schema=False)
def index():
    return {
        "ok": True,
        "name": "ABZ Agent API",
        "docs": "/docs",
        "chat": "POST /v1/chat",
        "message": "Backend connected — send requests via Next.js frontend or /v1/chat."
    }
