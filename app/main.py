# app/main.py
from __future__ import annotations

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.schemas import ChatRequest, ChatResponse, Message
from app.chatbot import run_sync  # sync function that calls abagentsdk Agent.run(...)

# -----------------------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME if hasattr(settings, "APP_NAME") else "ABZ Agent API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# -----------------------------------------------------------------------------
# CORS — allow your Vercel app + localhost. Regex covers any *.vercel.app domain.
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # keep empty when using regex
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# You can optionally add your exact prod/custom domain as well:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://your-custom-domain.com", "http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    """
    Lightweight liveness probe for uptime checks and cold-start prewarming.
    """
    return {"ok": True, "name": app.title, "status": "running"}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Accepts a list of messages [{role, content}], runs the ABZ agent,
    and returns the assistant's message. We offload the sync agent call
    to a worker thread so the event loop stays responsive.
    """
    try:
        # pydantic models -> plain dicts
        messages = [m.model_dump() for m in req.messages]

        # run_sync(...) is synchronous; execute in a thread
        answer: str = await asyncio.to_thread(run_sync, messages)
        return ChatResponse(message=Message(role="assistant", content=answer))

    except HTTPException:
        # pass through explicit HTTPExceptions
        raise
    except Exception as e:
        # keep error observable but not noisy
        raise HTTPException(status_code=500, detail=f"Agent Error: {e}")

@app.get("/", include_in_schema=False)
def index():
    """
    Friendly index for quick smoke testing.
    """
    return {"ok": True, "routes": ["/health", "POST /v1/chat", "/docs"]}

# -----------------------------------------------------------------------------
# Optional local dev entrypoint
# Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
