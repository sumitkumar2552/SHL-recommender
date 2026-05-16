
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from contextlib import asynccontextmanager
import uvicorn

from app.agent import chat
from app.retriever import get_retriever


# ── Startup: catalog + FAISS index load  ──────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Loading SHL catalog and building FAISS index...")
    try:
        get_retriever()          # singleton
        print("[Startup] Ready!")
    except FileNotFoundError as e:
        print(f"[Startup] ERROR: {e}")
        print("Run: python scraper/fallback_catalog.py   then restart.")
    yield                        # server running

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational agent to recommend SHL Individual Test Solutions.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response models ─────────────────────────────────────────────────
class Message(BaseModel):
    role: str       # "user" or "assistant"
    content: str

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        return v


class ChatRequest(BaseModel):
    messages: list[Message]

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v):
        if not v:
            raise ValueError("messages list cannot be empty")
        return v


class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Readiness check — evaluator yahi hit karta hai pehle."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Stateless chat endpoint.
    Har call mein poori conversation history bhejo.
    """
    # Turn cap: max 8 turns (user + assistant combined)
    if len(request.messages) > 8:
        raise HTTPException(
            status_code=400,
            detail="Conversation exceeds maximum 8 turns. Start a new conversation."
        )

    # convert Pydantic models into plain dicts 
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    result = chat(messages)

    return ChatResponse(
        reply=result["reply"],
        recommendations=[
            Recommendation(
                name=r["name"],
                url=r["url"],
                test_type=r["test_type"]
            )
            for r in result.get("recommendations", [])
        ],
        end_of_conversation=result.get("end_of_conversation", False)
    )


# ── Local run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
