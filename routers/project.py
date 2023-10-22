import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette import status
from .auth import get_current_user, get_mongo_client
from typing import Annotated
from bson.objectid import ObjectId
from dotenv import load_dotenv
from utils.vector_db import create_vector_database, add_to_vector_database
import logging
from models.request_models import CreateProjectRequest
from langchain.embeddings import HuggingFaceBgeEmbeddings
from models.db_models import Project, Chat, Source, Uploads
import shutil

router = APIRouter(
    prefix="/project",
    tags=["Project"]
)

load_dotenv()
logger = logging.getLogger(__name__)
handler = logging.FileHandler("logs/project.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

user_dependency = Annotated[dict, Depends(get_current_user)]
client = get_mongo_client()
PROJECT_COLLECTION = client[os.environ['DATABASE']]["project"]
EMBEDDINGS = HuggingFaceBgeEmbeddings(model_name=os.environ["EMBEDDINGS_MODEL"])

try:
    client.admin.command('ping')
    logger.info("Project connected to MongoDB!")
except Exception as e:
    logger.exception(e)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_projects(user: user_dependency):
    """Get projects of a user"""
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    projects_to_return = []
    projects = PROJECT_COLLECTION.find({"owner": user.get("id")})
    for project in projects:
        projects_to_return.append({
            "id":str(project.get("_id")),
            "topic":project.get("topic"),
            "subtopic":project.get("subtopic"),
            "resp_length":project.get("resp_length"),
        })

    return {"projects": projects_to_return}
    

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_single_project(user: user_dependency, id: str):
    """Get projects of a user"""
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    project = PROJECT_COLLECTION.find_one({"_id": ObjectId(id)})
    if str(project.get("owner"))!=user.get("id"):
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
    uploads_name_list = []
    for upload in project.get("uploads"):
        uploads_name_list.append(upload.get("name"))
    
    project_obj = Project(
        topic=project.get("topic"),
        subtopic=project.get("subtopic"),
        owner=project.get("owner"),
        resp_length=project.get("resp_length"),
        uploads=uploads_name_list,
        chats=project.get("chats")
    )
    return project_obj.__dict__
    

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_project(user: user_dependency, id: str):
    """Delete a project"""
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
    project = PROJECT_COLLECTION.find_one({"_id": ObjectId(id)})
    if str(project.get("owner"))!=user.get("id"):
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
    vector_db_path = f"{os.environ['VECTOR_DATABASES_FOLDER']}/{id}"
    if os.path.exists(vector_db_path):
        shutil.rmtree(vector_db_path)
    PROJECT_COLLECTION.delete_one({"_id": ObjectId(id)})


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def modify_project_detail(user: user_dependency, id: str, createProjectRequest: CreateProjectRequest):
    """Delete a project"""
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
    project = PROJECT_COLLECTION.find_one({"_id": ObjectId(id)})
    if str(project.get("owner"))!=user.get("id"):
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
    update = {
        "$set": {
            "topic": createProjectRequest.topic,
            "subtopic": createProjectRequest.subtopic,
            "resp_length": createProjectRequest.resp_length
        }
    }
    PROJECT_COLLECTION.find_one_and_update({"_id": ObjectId(id)}, update=update)


@router.post("/{id}/docs", status_code=status.HTTP_201_CREATED)
async def upload_docs(user: user_dependency, id: str, file: UploadFile):
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    project = PROJECT_COLLECTION.find_one({"_id": ObjectId(id)})
    if str(project.get("owner"))!=user.get("id"):
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    for upload in project.get("uploads"):
        if file.filename==upload["name"]:
            raise HTTPException(detail="file already uploaded", status_code=status.HTTP_406_NOT_ACCEPTABLE)

    file_path = f"temp_files/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    ids = add_to_vector_database(id, EMBEDDINGS, file_path)
    os.remove(file_path)
    filter = {"_id": ObjectId(id)}
    update = {
        "$push": {
            "uploads": Uploads(
                name=file.filename,
                id_list=ids
            ).__dict__
        }
    }
    PROJECT_COLLECTION.update_one(filter=filter, update=update)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_project(user: user_dependency, createProjectRequest: CreateProjectRequest):
    """Create a new project"""
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    project = Project(
        topic=createProjectRequest.topic,
        subtopic=createProjectRequest.subtopic,
        resp_length=createProjectRequest.resp_length,
        owner=user.get("id"),
    )
    project = PROJECT_COLLECTION.insert_one(project.__dict__)
    create_vector_database(project_id=str(project.inserted_id), embeddings=EMBEDDINGS)
    return {"project_id": str(project.inserted_id)}