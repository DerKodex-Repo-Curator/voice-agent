from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ChatMessageRequest(BaseModel):
    company_id: UUID
    session_id: Optional[UUID] = None
    message: str
    channel: str = "web"
