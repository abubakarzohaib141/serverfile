"""
This file is intentionally left blank for the actual ABZ Agent integration.

PLEASE BUILD IT BY YOURSELF:
- Import abagentsdk
- Construct your Agent (Gemini-only per your product)
- Implement an async function `run_agent(messages: list[dict]) -> str`
"""

from typing import List, Dict

class NotImplementedAgent(Exception):
    pass

async def run_agent(messages: List[Dict[str, str]]) -> str:
    # DO NOT implement now (per request).
    # Raise a clear message so you know exactly where to code later.
    raise NotImplementedAgent(
        "Please build it by myself: integrate abagentsdk Agent here."
    )
