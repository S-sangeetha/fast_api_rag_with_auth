# RAG Chatbot API

A multi-source Retrieval-Augmented Generation (RAG) chatbot built with **FastAPI, MongoDB Atlas Vector Search, Google Gemini, and WebSocket**.

The application allows users to authenticate, upload documents, process different types of content, generate embeddings, store document chunks in MongoDB, and ask questions using a Multi-RAG pipeline.

The system can retrieve information from different source types such as **text, image, and audio**, combine semantic and keyword search using **Hybrid Search + Reciprocal Rank Fusion (RRF)**, rerank the retrieved results, and generate grounded answers using an LLM.

---

## Features

### Authentication

- JWT authentication
- User registration and login
- Access tokens
- Refresh tokens
- Protected APIs

### Document Processing

- Document upload
- TXT text extraction
- PDF text extraction
- Image OCR
- Audio transcription
- Text chunking
- Metadata extraction

### RAG

- Gemini embeddings
- MongoDB Atlas Vector Search
- Semantic search
- Keyword search
- Hybrid search
- Reciprocal Rank Fusion (RRF)
- Result deduplication
- LLM-based reranking
- Context building
- Source references
- Multi-source question answering

### Multi-RAG

The system can determine which source types are required to answer a question.

Supported source types:

```text
text
image
audio