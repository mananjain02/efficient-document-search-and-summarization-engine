from fastapi import FastAPI
from routers import auth, project, chat, feedback
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

app = FastAPI()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(chat.router)
app.include_router(feedback.router)

