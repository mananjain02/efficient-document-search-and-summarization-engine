from pydantic import BaseModel

class TokenResponse(BaseModel):
    name: str
    access_token: str
    token_type: str