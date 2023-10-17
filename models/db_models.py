from typing import Optional, List
from datetime import datetime

class User:
    id: Optional[any] = None
    name: str
    email: str
    hashed_password: str
    role: str

    def __init__(self, name, email, hashed_password, role, id=None) -> None:
        if id!=None:
            self.id = id
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
        self.role = role

class Source:
    id: Optional[any] = None
    text: str
    name: str
    page: Optional[int] = None

    def __init__(self, text, name, id=None, page=0) -> None:
        if id!=None:
            self.id = id
        
        if page!=None:
            self.page = page
        
        self.text = text
        self.name = name

class Chat:
    id: Optional[any] = None
    timestamp: int
    sender: str
    text: str
    source: Optional[List[Source]]

    def __init__(self, sender, text, source=None) -> None:
        if source!=None:
            self.source=source
        self.timestamp = int(datetime.now().timestamp())
        self.sender = sender
        self.text = text

class Uploads:
    id: Optional[any] = None
    name: str
    id_list: List[str]
    timestamp: int

    def __init__(self, name, id_list, id=None) -> None:
        if id!=None:
            self.id = id
        
        self.name = name
        self.id_list = id_list
        self.timestamp = int(datetime.now().timestamp())

class Project:
    id: Optional[any] = None
    topic: str
    subtopic: str
    resp_length: str
    owner: str
    created_at: int
    chats: Optional[List[Chat]] = None
    uploads: Optional[List[Uploads]]

    def __init__(self, topic, resp_length, owner, subtopic="", id=None, chats=[], uploads=[]) -> None:
        if id!=None:
            self.id=id

        self.subtopic = subtopic
        self.owner = owner
        self.chats = chats
        self.topic = topic
        self.resp_length = resp_length
        self.created_at = int(datetime.now().timestamp())
        self.uploads = uploads
