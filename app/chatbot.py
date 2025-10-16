# app/chatbot.py
import os
from functools import lru_cache
from typing import List, Dict

from dotenv import load_dotenv

# load GEMINI_API_KEY from .env or environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is Missing — set your API key in environment variables or .env"
    )

from abagentsdk import Agent, Memory, function_tool

# optional tool example
@function_tool()
def current_time(tz: str = "UTC") -> str:
    """Return current time in the given timezone (IANA, e.g. 'America/Los_Angeles')."""
    from datetime import datetime
    try:
        import zoneinfo  # tzdata should be installed; works on Windows too
        now = datetime.now(zoneinfo.ZoneInfo(tz))
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return "Invalid timezone. Try 'UTC' or 'America/Los_Angeles'."

SYSTEM_PROMPT = (
    "You are the ABZ Website Chatbot. "
    "Be concise, helpful, and friendly. "
    "Use the 'current_time' tool when the user asks for time in a specific timezone. "
    "Do NOT reveal internal JSON/tool calls—return final answers only."
    "Here are some details about ABZ Agent SDK – The Fastest Way to Build AI Agents: "
    "I developed ABZ Agent SDK to simplify building AI agents. While OpenAI recently launched their own Agent SDK, it requires a paid API and involves hard coding to connect Gemini (Google API). With ABZ Agent SDK, connecting Gemini is seamless—just load your API key, and you're ready to go. This makes it faster and more accessible for developers to build and scale agentic systems."
)

@lru_cache(maxsize=1)
def get_agent() -> Agent:
    """Create a singleton Agent (cached across requests)."""
    return Agent(
        name="ABZ Chatbot",
        instructions=SYSTEM_PROMPT,
        model="gemini-2.0-flash",
        tools=[current_time],  # remove if you don't want tools
        memory=Memory(),       # persistent, in-process
        verbose=False,
        max_iterations=3,
        api_key=GEMINI_API_KEY,  # uses YOUR env key
    )

async def run_agent(messages: List[Dict[str, str]]) -> str:
    """
    Bridge for FastAPI.
    - messages: [{"role": "user"|"assistant"|"system", "content": "..."}]
    - We’ll pass only the latest user message to Agent.run();
      the Agent has Memory() so it keeps context across calls.
    """
    agent = get_agent()
    # pull the last user message; fallback to last message
    user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), None)
    if not user_msg:
        user_msg = messages[-1]["content"]
    res = agent.run(user_msg)
    return res.content

# ----- Optional CLI for local dev -----
def main():
    agent = get_agent()
    print("🤖 ABZ Chatbot ready. Type 'exit' to quit.")
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye.")
            break

        if user.lower() in {"exit", "quit"}:
            print("👋 Bye.")
            break

        try:
            res = agent.run(user)
            print(f"Bot: {res.content}")
        except Exception as e:
            print(f"Bot: [Error] {e}")

if __name__ == "__main__":
    main()
