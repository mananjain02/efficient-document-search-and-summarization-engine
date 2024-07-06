# Efficient Document Search and Summarization Engine

## Overview

The **Efficient Document Search and Summarization Engine** is a powerful tool designed to enhance research efficiency and clarity by integrating advanced Large Language Models (LLMs) such as ChatGPT and LLAMA. This project leverages cutting-edge technologies to provide a seamless and efficient document search and summarization experience.

## Features

- **LLM Integration**: Utilizes leading LLMs to summarize research findings, enhancing the efficiency and clarity of research output.
- **RESTful API**: Offers a robust API for document and query retrieval, ensuring optimized and accurate search results.
- **Vector Databases**: Implements vector databases for efficient storage and retrieval, improving search performance.
- **Advanced Algorithms**: Applies cosine similarity and k-means clustering to ensure precise text extraction and query matching.

## Technologies Used

- **Python**: Core programming language for development.
- **FastAPI**: Framework for building the RESTful API.
- **Langchain**: Toolchain for integrating language models.
- **MongoDB**: Database for storing documents and metadata.
- **Pinecone**: Vector database for optimized query storage and retrieval.

## Installation

To set up the project locally, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/mananjain02/efficient-document-search-and-summarization-engine.git
    cd efficient-document-search-and-summarization-engine
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
    Create a `.env` file in the root directory and add your configuration settings.
    ```env
    MONGODB_URL=<mongo-db-uri>
    SECRET_KEY=<bcrypt-key>
    ALGORITHM="HS256"
    DATABASE=<database-name>
    EMBEDDINGS_MODEL="BAAI/bge-large-en-v1.5"
    VECTOR_DATABASES_FOLDER="vector_databases"
    OPENAI_API_KEY=<open-ai-key-if-want-to-use-chatgpt>
    TOKENIZERS_PARALLELISM="False"
    ```

5. **Run the Application**:
    ```bash
    uvicorn main:app --reload
    ```

## Usage

### API Documentation

API documentation and further details can be accessed using Swagger. Once the application is running, navigate to `http://localhost:8000/docs` to explore and interact with the API endpoints.
