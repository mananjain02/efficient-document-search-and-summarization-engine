from pydantic import BaseModel
from typing import Optional, List, Any

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        json_schema_extra = {
            'example': {
                "name": "manan jain",
                "email": "test@example.com",
                "password": "password123"
            }
        }

class CreateProjectRequest(BaseModel):
    topic: str
    subtopic: Optional[str] = None
    resp_length: str


class ChatRequest(BaseModel):
    query: str
    history: List[Any]

class FeebackRequest(BaseModel):
    feedback: str