import os
from fastapi import APIRouter, Depends, HTTPException
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.chat_models import ChatOpenAI
from utils.chat_utils import get_prompt
from bson.objectid import ObjectId
from langchain.vectorstores import FAISS
from .auth import get_current_user, get_mongo_client
from starlette import status
from typing import Annotated
from models.request_models import ChatRequest
from models.db_models import Chat, Project, Source
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]
client = get_mongo_client()
PROJECT_COLLECTION = client[os.environ['DATABASE']]["project"]
EMBEDDINGS = HuggingFaceBgeEmbeddings(model_name=os.environ["EMBEDDINGS_MODEL"])
LLM = ChatOpenAI()

@router.post("/{id}")
async def chat(user: user_dependency, id: str, chatRequest: ChatRequest):
    if user is None:
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    project = PROJECT_COLLECTION.find_one({"_id": ObjectId(id)})
    if str(project.get("owner"))!=user.get("id"):
        raise HTTPException(detail="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
    vectorstore = FAISS.load_local(f"{os.environ['VECTOR_DATABASES_FOLDER']}/{id}", embeddings=EMBEDDINGS)
    chain = ConversationalRetrievalChain.from_llm(
        llm=LLM,
        chain_type='stuff',
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True
    )
    history = []
    ind = 0
    while ind < len(chatRequest.history):
        history.append((chatRequest.history[ind], chatRequest.history[ind+1]))
        ind+=2
    
    prompt = get_prompt(project.get("topic"), project.get("subtopic"), project.get("resp_length"),  chatRequest.query, "English")
    response = chain({"question": prompt, "chat_history": history})
    source_list = []
    for source in response["source_documents"]:
        source_list.append(Source(
            text=source.page_content,
            name=source.metadata["source"],
            page=source.metadata["page"]
        ).__dict__)
    user_chat = Chat(
        sender="human",
        text=chatRequest.query,
    )
    bot_chat = Chat(
        sender="bot",
        text=response["answer"],
        source=source_list
    )
    filter = {"_id": ObjectId(id)}
    update = {
        "$push": {
            "chats": user_chat.__dict__
        }
    }
    PROJECT_COLLECTION.update_one(filter=filter, update=update)
    update = {
        "$push": {
            "chats": bot_chat.__dict__
        }
    }
    PROJECT_COLLECTION.update_one(filter=filter, update=update)
    return bot_chat.__dict__

    

