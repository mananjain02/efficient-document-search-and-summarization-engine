import os
from fastapi import Depends, APIRouter, HTTPException
from .auth import get_current_user, get_mongo_client
from typing import Annotated
from models.request_models import FeebackRequest
from starlette import status

router = APIRouter(
    prefix="/feedback",
    tags=["Feeback"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]
client = get_mongo_client()
client = get_mongo_client()
FEEDBACK_COLLECTION = client[os.environ['DATABASE']]["feedback"]

@router.post("/", status_code=status.HTTP_201_CREATED)
def save_feeback(user: user_dependency, feebackRequest: FeebackRequest):
    if user is None:
        raise HTTPException(detail="unauthorized")
    
    FEEDBACK_COLLECTION.insert_one({
        "feedback": feebackRequest.feedback,
        "owner": user.get("id")
    })