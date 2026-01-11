from pydantic import BaseModel
from typing import Dict, Any


class ChatRequest(BaseModel):
    user_message: str
    profile: Dict[str, Any]