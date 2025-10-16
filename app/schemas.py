from pydantic import BaseModel, Field
from typing import Literal, List, Optional

Role = Literal["system", "user", "assistant"]

class Message(BaseModel):
    role: Role
    content: str = Field(..., min_length=1)

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1)

class ChatResponse(BaseModel):
    message: Message
