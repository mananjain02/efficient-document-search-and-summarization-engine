import os
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from .text_splitters import sentence_splitter
from langchain.text_splitter import SpacyTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv
load_dotenv()
VECTOR_DATABASES_FOLDER=os.environ['VECTOR_DATABASES_FOLDER']


def create_vector_database(project_id: str, embeddings: any):
    document = Document(
        page_content=project_id,
        metadata={
            "source": "project_id",
            "page": 0
        }
    )
    db = FAISS.from_documents([document], embedding=embeddings)
    db.save_local(folder_path=f"{VECTOR_DATABASES_FOLDER}/{project_id}")

def add_to_vector_database(project_id: str, embeddings: any, file_path: str) -> [str]:
    print("Indexing")
    """Adds document to vector database and returns list of ids"""
    text_from_doc = []
    extension = file_path.split('.')[-1]
    loader = None
    if extension=="pdf":
        loader = PyPDFLoader(file_path=file_path)
        text_from_doc.extend(loader.load())

    for doc in text_from_doc:
        doc.metadata["source"] = doc.metadata["source"].split("/")[-1]

    # naive text splitter
    # text_chunks = sentence_splitter(text_from_doc)

    # spcay text splitter
    text_splitter = SpacyTextSplitter()
    text_chunks = text_splitter.split_documents(text_from_doc)
    vector_db = FAISS.load_local(f"{VECTOR_DATABASES_FOLDER}/{project_id}", embeddings=embeddings)
    ids = vector_db.add_documents(text_chunks)
    vector_db.save_local(f"{VECTOR_DATABASES_FOLDER}/{project_id}")
    return ids
        



