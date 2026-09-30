# Personal Knowledge AI

A full-stack personal knowledge and AI chat application built with **Django**, **Django REST Framework**, **JavaScript**, **Groq AI**, and local **sentence-transformer embeddings**.

Personal Knowledge AI allows users to create an account, manage multiple AI conversations, upload personal documents, extract and index their content, search them semantically, and ask AI questions grounded in their own knowledge base.

The project is being developed as a portfolio application focused on modern Python web development, REST APIs, authentication, frontend-backend communication, AI integration, semantic search, embeddings, and Retrieval-Augmented Generation (RAG).

---

## ✨ Current Features

### 🔐 Authentication

Users can create and access their own accounts.

Current authentication functionality includes:

- User registration
- User login
- User logout
- Custom Django User model
- Session-based authentication
- CSRF protection
- Protected frontend pages
- User-specific conversations
- User-specific documents

Each user can only access their own chats, messages, and document library.

---

## 💬 AI Chat

Users can communicate with an AI assistant directly through the application.

The chat system currently supports:

- Sending user messages
- Receiving AI-generated responses
- Saving user messages
- Saving assistant messages
- Conversation context
- Persistent chat history
- Markdown-formatted AI responses
- Code syntax highlighting
- Copy code buttons
- AI thinking/loading indicator
- Automatic RAG lookup against personal documents
- Normal AI fallback when no relevant document context is found
- Document source metadata for RAG responses

The AI receives recent messages from the conversation so it can understand follow-up questions and maintain context.

---

## 🤖 Groq AI Integration

The main language model layer is powered by **Groq** through an OpenAI-compatible Python client.

Current AI model:

```text
openai/gpt-oss-120b
```

The AI integration is separated into service modules:

```text
apps/
└── ai/
    └── services/
        ├── ai_service.py
        └── rag_service.py
```

### `ai_service.py`

Responsible for normal AI conversation generation.

### `rag_service.py`

Responsible for:

- Semantic document retrieval
- Building document context
- Sending grounded context to the AI
- Returning document-based answers
- Returning source metadata

This keeps AI provider logic and RAG logic separate from Django views.

---

## 🗂️ Multiple Chats

Users can create and manage multiple conversations.

Current chat functionality includes:

- Create a new chat
- View existing chats
- Select a conversation
- Load conversation history
- Continue previous conversations
- Automatic chat titles
- Rename conversations
- Delete conversations
- User-specific chat ownership

Example:

```text
My Chats
│
├── Django Learning
├── Python Questions
├── REST API
└── New Chat
```

Each chat belongs to the currently authenticated user.

---

## 📜 Chat History

Messages are stored in the database.

Each message can contain:

```text
Message
├── Chat
├── Role
├── Content
├── Sources
└── Created At
```

Supported message roles:

```text
user
assistant
system
```

RAG-generated assistant messages can also store document source metadata.

Example:

```json
[
  {
    "document_id": 3,
    "document_title": "Python Notes",
    "chunk_index": 0,
    "score": 0.858778
  }
]
```

This allows conversations and document references to persist between page reloads.

---

# 📚 Personal Document Library

Users can upload and manage their own personal documents.

Currently supported formats:

```text
PDF
TXT
Markdown (.md)
```

Current upload limit:

```text
10 MB per file
```

Document functionality includes:

- Upload documents
- Personal document library
- Rename documents
- Delete documents
- Protected document download
- File metadata
- Text extraction
- Extraction status
- Indexing status
- Automatic chunk generation
- Automatic embedding generation

Each uploaded document belongs to the authenticated user.

---

## 📄 Document Text Extraction

Uploaded documents are automatically processed after upload.

Supported extraction:

### TXT

Plain UTF-8 text extraction.

### Markdown

Markdown source text is preserved for later retrieval.

### PDF

Text is extracted using `pypdf`.

The system tracks extraction state:

```text
pending
ready
failed
```

Example:

```text
Python Notes
TXT · 246 B · Text ready
```

Scanned image-only PDFs currently require OCR and may return an extraction failure.

OCR is not implemented yet.

---

# ✂️ Document Chunking

Long document text is divided into smaller text sections called **chunks**.

Chunking allows the system to retrieve only the parts of a document that are relevant to a user's question instead of sending the entire document to the AI.

Current chunking configuration uses:

```text
Chunk size: 400 characters
Chunk overlap: 60 characters
```

The overlap helps preserve context between neighboring chunks.

Example:

```text
Document
    ↓
Chunk 0
Chunk 1
Chunk 2
Chunk 3
...
```

Each chunk is stored in the database using the `DocumentChunk` model.

---

# 🧠 Embeddings

Every document chunk is converted into a numerical vector representation called an **embedding**.

Embeddings allow the application to compare text by meaning instead of relying only on exact keyword matches.

Current embedding model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Embedding dimensions:

```text
384
```

Example:

```text
Document Chunk
      ↓
Embedding Model
      ↓
[0.012, -0.038, 0.091, ...]
```

Embeddings are currently generated locally through `sentence-transformers`.

They are stored in the database with each document chunk.

---

# ⚙️ Automatic Document Indexing

Document indexing happens automatically after successful text extraction.

Current pipeline:

```text
Upload document
      ↓
Save original file
      ↓
Extract text
      ↓
Text ready
      ↓
Split into chunks
      ↓
Generate embeddings
      ↓
Save DocumentChunk records
      ↓
Embeddings ready
```

The system tracks indexing status separately:

```text
pending
ready
failed
```

Example Library status:

```text
PDF · 150 KB · Text ready · Embeddings ready
```

---

# 🔎 Semantic Search

Personal Knowledge AI supports semantic search across indexed document chunks.

When a user submits a query:

```text
User Query
    ↓
Generate Query Embedding
    ↓
Compare With Document Chunk Embeddings
    ↓
Calculate Similarity
    ↓
Sort Results
    ↓
Return Most Relevant Chunks
```

The initial implementation calculates cosine similarity in Python.

Searches are filtered by authenticated user so one user's documents are never included in another user's semantic search.

A minimum similarity threshold is used to prevent weak document matches from being passed into the RAG pipeline.

---

# 🧩 Retrieval-Augmented Generation (RAG)

The application includes a working Retrieval-Augmented Generation pipeline.

RAG allows the AI assistant to answer questions using the user's own documents.

Current RAG flow:

```text
User Question
      ↓
Semantic Search
      ↓
Relevant Document Chunks
      ↓
Build Context
      ↓
Groq / GPT-OSS
      ↓
Grounded AI Answer
      ↓
Document Sources
```

Example question:

```text
What is Django REST Framework?
```

Relevant document chunk:

```text
Django REST Framework is used to build REST APIs.
```

Example answer:

```text
Django REST Framework is a tool used to build REST APIs.

Source: Python Notes
```

The system also returns structured source metadata:

```json
{
  "document_id": 3,
  "document_title": "Python Notes",
  "chunk_index": 0,
  "score": 0.858778
}
```

---

# 🔄 RAG + Normal Chat Fallback

The main chat automatically attempts document retrieval before generating a response.

Current flow:

```text
User Message
      ↓
Semantic Search
      ↓
Relevant document found?
   ↙               ↘
 YES               NO
  ↓                 ↓
RAG Answer      Normal AI Chat
  ↓                 ↓
  └────── AI Response ──────┘
```

If a relevant personal document is found, the AI generates a document-grounded response.

If no sufficiently relevant document is found, the application falls back to the normal AI chat experience.

Example:

```text
Question:
What is Django REST Framework?

→ RAG
→ Source: Python Notes
```

But:

```text
Question:
What is the capital of Japan?

→ No relevant personal document
→ Normal AI response
```

---

# 🌐 REST API

The backend exposes REST API endpoints using **Django REST Framework**.

## Authentication

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
```

---

## Chats

```http
GET    /api/chats/
POST   /api/chats/

GET    /api/chats/{id}/
PATCH  /api/chats/{id}/
DELETE /api/chats/{id}/
```

---

## Messages

```http
GET  /api/chats/{id}/messages/
POST /api/chats/{id}/messages/
```

Example message request:

```json
{
  "content": "What is Django REST Framework?"
}
```

Example RAG-enabled response:

```json
{
  "user_message": {
    "id": 10,
    "role": "user",
    "content": "What is Django REST Framework?"
  },
  "assistant_message": {
    "id": 11,
    "role": "assistant",
    "content": "Django REST Framework is a tool used to build REST APIs.",
    "sources": [
      {
        "document_id": 3,
        "document_title": "Python Notes",
        "chunk_index": 0,
        "score": 0.858778
      }
    ]
  }
}
```

---

## Documents

```http
GET    /api/documents/
POST   /api/documents/

GET    /api/documents/{id}/
PATCH  /api/documents/{id}/
DELETE /api/documents/{id}/

GET    /api/documents/{id}/download/
```

Document upload automatically triggers:

```text
Text Extraction
→ Chunking
→ Embeddings
→ Indexing
```

---

## Semantic Search

```http
POST /api/documents/search/
```

Example request:

```json
{
  "query": "What is Django REST Framework?",
  "limit": 5
}
```

Example response:

```json
{
  "query": "What is Django REST Framework?",
  "count": 1,
  "results": [
    {
      "document_id": 3,
      "document_title": "Python Notes",
      "chunk_index": 0,
      "score": 0.858778,
      "content": "Django REST Framework is used to build REST APIs."
    }
  ]
}
```

---

## Ask Documents / RAG

```http
POST /api/documents/ask/
```

Example request:

```json
{
  "question": "What is Django REST Framework?",
  "limit": 5,
  "min_score": 0.30
}
```

Example response:

```json
{
  "answer": "Django REST Framework is a tool used to build REST APIs.",
  "sources": [
    {
      "document_id": 3,
      "document_title": "Python Notes",
      "chunk_index": 0,
      "score": 0.858778
    }
  ]
}
```

---

# 🖥️ Frontend

The application includes a custom responsive frontend built with:

- HTML
- CSS
- Bootstrap
- JavaScript
- Fetch API
- AJAX
- Django Templates
- Marked
- DOMPurify
- Highlight.js

Current interface includes:

- Login page
- Registration page
- Chat page
- Personal Library page
- Conversation sidebar
- Responsive mobile sidebar
- New Chat button
- Rename conversation
- Delete conversation
- Message history
- User messages
- AI messages
- Markdown rendering
- Code syntax highlighting
- Copy code buttons
- AI thinking/loading animation
- Message input
- Send button
- Logout button
- Responsive mobile interface
- Document upload form
- Document list
- Rename document
- Delete document
- Document extraction status
- Document indexing status

---

# ⚡ Chat Flow

When a user sends a message:

```text
User enters message
        ↓
JavaScript
        ↓
Display user message
        ↓
Show AI thinking indicator
        ↓
fetch()
        ↓
POST /api/chats/{id}/messages/
        ↓
Django REST Framework
        ↓
Save user message
        ↓
Semantic Search
        ↓
Relevant document found?
     ↙              ↘
   YES               NO
    ↓                 ↓
 RAG Context      Chat History
    ↓                 ↓
    └────── Groq AI ──┘
              ↓
      Generate response
              ↓
   Save assistant message
              ↓
       Save sources
              ↓
        JSON response
              ↓
         JavaScript
              ↓
Remove loading indicator
              ↓
     Render AI message
```

---

# 📚 Document Processing Flow

When a user uploads a document:

```text
User selects file
        ↓
POST /api/documents/
        ↓
Save file
        ↓
Extract document text
        ↓
extraction_status = ready
        ↓
Split into chunks
        ↓
Generate embeddings
        ↓
Store DocumentChunk records
        ↓
indexing_status = ready
        ↓
Document becomes searchable
```

---

# 🏗️ Project Architecture

```text
Personal-Knowledge-AI/
│
├── apps/
│   │
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── chats/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── utils.py
│   │
│   ├── documents/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── signals.py
│   │   └── services/
│   │       ├── extraction.py
│   │       ├── chunking.py
│   │       ├── embeddings.py
│   │       ├── indexing.py
│   │       ├── indexing_pipeline.py
│   │       └── search.py
│   │
│   ├── ai/
│   │   └── services/
│   │       ├── ai_service.py
│   │       └── rag_service.py
│   │
│   └── frontend/
│       ├── templates/
│       │   └── frontend/
│       │       ├── base.html
│       │       ├── chat.html
│       │       ├── library.html
│       │       ├── login.html
│       │       └── register.html
│       │
│       └── static/
│           └── frontend/
│               ├── css/
│               │   └── app.css
│               │
│               └── js/
│                   ├── chat.js
│                   ├── library.js
│                   ├── login.js
│                   └── register.js
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🛠️ Tech Stack

## Backend

- Python
- Django
- Django REST Framework

## Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript
- Fetch API
- AJAX
- Django Templates
- Marked
- DOMPurify
- Highlight.js

## Database

- SQLite

## AI

- Groq API
- OpenAI-compatible Python SDK
- GPT-OSS

## Document Processing

- pypdf
- sentence-transformers

## Embeddings

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## Development

- PyCharm Professional
- Git
- GitHub
- Python Virtual Environment

---

# 🔒 Environment Variables

Sensitive data is stored using environment variables.

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-django-secret-key
DEBUG=True

GROQ_API_KEY=your-groq-api-key
AI_MODEL=openai/gpt-oss-120b
```

The repository contains `.env.example` instead:

```env
DJANGO_SECRET_KEY=your-django-secret-key
DEBUG=True

GROQ_API_KEY=your-groq-api-key
AI_MODEL=openai/gpt-oss-120b
```

Never commit the real `.env` file or production secrets.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <repository-url>
```

Move into the project:

```bash
cd Personal-Knowledge-AI
```

---

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create:

```text
.env
```

using:

```text
.env.example
```

as a template.

---

## 5. Apply migrations

```bash
python manage.py migrate
```

---

## 6. Run the application

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# ✅ Current Project Status

```text
✅ Django project architecture
✅ Custom User model
✅ User registration
✅ User login
✅ User logout
✅ Session authentication

✅ Django REST Framework
✅ Authentication REST API
✅ Chat REST API
✅ Message REST API
✅ Document REST API
✅ Semantic search API
✅ RAG API

✅ Create new chat
✅ Multiple conversations
✅ Chat history
✅ User-specific chats
✅ Automatic chat titles
✅ Rename conversations
✅ Delete conversations

✅ Groq AI integration
✅ AI-generated responses
✅ Conversation context
✅ User and assistant message persistence
✅ Normal AI fallback

✅ Personal document library
✅ Document uploads
✅ PDF support
✅ TXT support
✅ Markdown support
✅ Protected document access
✅ Document text extraction

✅ Document chunking
✅ Embeddings
✅ Automatic indexing
✅ Semantic search
✅ Similarity-based retrieval

✅ Retrieval-Augmented Generation
✅ Ask questions about documents
✅ AI-generated answers grounded in documents
✅ Document source metadata
✅ RAG integration with main chat

✅ HTML frontend
✅ CSS styling
✅ Bootstrap
✅ JavaScript
✅ Fetch / AJAX
✅ Login interface
✅ Registration interface
✅ Chat interface
✅ Library interface
✅ Conversation sidebar
✅ New Chat
✅ Send / receive messages
✅ Markdown rendering
✅ Code syntax highlighting
✅ Copy code buttons
✅ Improved loading states
✅ Responsive mobile interface
```

---

# 🗺️ Planned Improvements

## Personal Knowledge & RAG

```text
✅ Document uploads
✅ Personal document library
✅ Document text extraction
✅ Document chunking
✅ Embeddings
✅ Automatic indexing
✅ Semantic search
✅ RAG
✅ Ask questions about documents
✅ AI-generated answers with sources

⬜ Improved source display in chat UI
⬜ Clickable document sources
⬜ Better chunking strategy
⬜ Token-aware chunking
⬜ Search quality tuning
⬜ Configurable similarity threshold
⬜ OCR for scanned PDFs
⬜ Additional document formats
```

## Search & Vector Infrastructure

```text
⬜ PostgreSQL
⬜ pgvector
⬜ Database-level vector search
⬜ Faster retrieval for large libraries
⬜ Document-level filtering
⬜ Hybrid semantic + keyword search
```

## Background Processing

```text
⬜ Background document processing
⬜ Background embedding generation
⬜ Job status tracking
⬜ Retry failed indexing jobs
```

## Engineering & Production

```text
⬜ Automated tests
⬜ API integration tests
⬜ RAG retrieval tests
⬜ PostgreSQL
⬜ Docker
⬜ Production deployment
⬜ Logging and monitoring
```

---

# 🎯 Project Goal

The long-term goal of **Personal Knowledge AI** is to become a personal knowledge assistant capable of working with a user's own conversations, documents, and knowledge base.

```text
Personal Knowledge AI
        │
        ├── AI Chat
        │
        ├── Chat History
        │
        ├── Personal Library
        │
        ├── Documents
        │       ↓
        │   Text Extraction
        │       ↓
        │   Chunking
        │       ↓
        │   Embeddings
        │
        ├── Semantic Search
        │
        └── RAG
                ↓
        Grounded AI Answers
                ↓
              Sources
```

---

# 📌 Development Status

The project is under active development.

The main application pipeline is now working end-to-end:

```text
Authentication
      ↓
Responsive Frontend
      ↓
REST API
      ↓
Personal Document Library
      ↓
Text Extraction
      ↓
Document Chunking
      ↓
Embeddings
      ↓
Semantic Search
      ↓
RAG
      ↓
Groq AI
      ↓
Grounded AI Response
      ↓
Document Sources
```
