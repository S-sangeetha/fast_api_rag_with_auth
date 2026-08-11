# RAG Chatbot API

A Retrieval-Augmented Generation (RAG) chatbot built with **FastAPI, MongoDB Atlas Vector Search, and Google Gemini**.

The application allows users to upload documents, extract and chunk their content, generate embeddings, store them in MongoDB, and ask questions based on the uploaded documents.

## Features

- JWT authentication
- Document upload
- TXT and PDF text extraction
- Image OCR support
- Text chunking
- Gemini embeddings
- MongoDB Atlas Vector Search
- Semantic document search
- Gemini LLM-based answers
- Source references in responses
- Update existing documents

## Tech Stack

- Python
- FastAPI
- MongoDB / MongoDB Atlas Vector Search
- Google Gemini
- LangChain
- PyPDF
- Pillow
- Pytesseract
- JWT

## Project Structure

```text
chatbot/
│
├── src/
│   ├── api/
│   ├── service/
│   ├── models/
│   ├── database.py
│   ├── jwt_handler.py
│   ├── llm_config.py
│   └── main.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## RAG Flow

```text
Upload Document
      ↓
Extract Text
      ↓
Split into Chunks
      ↓
Generate Embeddings
      ↓
Store in MongoDB
```

For questions:

```text
User Question
      ↓
Generate Query Embedding
      ↓
MongoDB Vector Search
      ↓
Retrieve Relevant Chunks
      ↓
Build Context
      ↓
Gemini LLM
      ↓
Final Answer
```

## MongoDB Vector Search

The document chunks are stored with their embeddings:

```json
{
  "document_id": "unique-id",
  "file_name": "employee.txt",
  "chunk_index": 0,
  "text": "Employees are allowed 20 days of annual leave.",
  "embedding": []
}
```

MongoDB Atlas Vector Search is used to find the most relevant chunks for a user's question.

## Environment Variables

Create a `.env` file:

```env
MONGODB_URL=your_mongodb_connection_string
GOOGLE_API_KEY=your_google_api_key
JWT_SECRET_KEY=your_secret_key
```

## Installation

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
uvicorn src.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Main APIs

```text
POST /auth/login
POST /auth/refresh

POST /documents/upload

POST /search

POST /rag/chat
```

## Example

Question:

```text
How many days of annual leave are employees allowed?
```

Answer:

```text
Employees are allowed 20 days of annual leave.
```

The response also includes the document chunks used to generate the answer.

## Future Improvements

- Conversation history
- Streaming responses
- Better OCR
- Hybrid search
- Reranking
- Metadata filtering
- User-specific documents
- RAG evaluation