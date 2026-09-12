# Personal Knowledge AI

A full-stack AI chat application built with **Django**, **Django REST Framework**, **JavaScript**, and **Groq AI**.

Personal Knowledge AI allows users to create an account, start multiple conversations, send messages to an AI assistant, and keep their chat history saved.

The project is being developed as a portfolio application focused on modern Python web development, REST APIs, authentication, frontend-backend communication, and AI integration.

---

## ✨ Current Features

### 🔐 Authentication

Users can create and access their own accounts.

Current authentication functionality includes:

* User registration
* User login
* User logout
* Custom Django User model
* Session-based authentication
* Protected chat pages
* User-specific conversations

Each user can only access their own chats and messages.

---

### 💬 AI Chat

Users can communicate with an AI assistant directly through the application.

The chat system currently supports:

* Sending user messages
* Receiving AI-generated responses
* Saving user messages
* Saving assistant messages
* Conversation context
* Persistent chat history
* Markdown-formatted AI responses
* Code syntax highlighting
* AI thinking/loading indicator

The AI receives previous messages from the conversation so it can understand follow-up questions and maintain context.

---

### 🤖 Groq AI Integration

The AI layer is powered by **Groq**.

The application communicates with Groq through an OpenAI-compatible API client.

Current AI configuration uses:

```text
openai/gpt-oss-120b
```

The AI integration is separated into its own service layer:

```text
apps/
└── ai/
    └── services/
        └── ai_service.py
```

This keeps the AI provider logic separate from Django views and makes the architecture easier to maintain and extend.

---

### 🗂️ Multiple Chats

Users can create and manage multiple conversations.

Current chat functionality includes:

* Create a new chat
* View existing chats
* Select a conversation
* Load conversation history
* Continue previous conversations
* Automatic chat titles
* Rename conversations
* Delete conversations

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

### 📜 Chat History

Messages are stored in the database.

Each message contains:

```text
Chat
├── User
├── Role
├── Content
└── Created At
```

Supported message roles:

```text
user
assistant
system
```

The conversation structure is:

```text
User
 │
 └── Chat
      │
      ├── User Message
      ├── Assistant Message
      ├── User Message
      └── Assistant Message
```

This allows conversations to persist between page reloads.

---

### 🌐 REST API

The backend exposes REST API endpoints using **Django REST Framework**.

Current endpoints include:

#### Authentication

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/me/
```

#### Chats

```http
GET    /api/chats/
POST   /api/chats/

GET    /api/chats/{id}/
PATCH  /api/chats/{id}/
DELETE /api/chats/{id}/
```

#### Messages

```http
GET  /api/chats/{id}/messages/
POST /api/chats/{id}/messages/
```

Example message request:

```json
{
  "content": "Explain Django REST Framework."
}
```

Example response:

```json
{
  "user_message": {
    "id": 1,
    "role": "user",
    "content": "Explain Django REST Framework."
  },
  "assistant_message": {
    "id": 2,
    "role": "assistant",
    "content": "Django REST Framework is..."
  }
}
```

---

## 🖥️ Frontend

The application includes a custom responsive frontend built with:

* HTML
* CSS
* Bootstrap
* JavaScript
* Fetch API
* AJAX
* Django Templates

The frontend communicates with the Django REST API without reloading the page for every action.

Current interface includes:

* Login page
* Registration page
* Chat page
* Conversation sidebar
* Responsive mobile sidebar
* New Chat button
* Rename conversation
* Delete conversation
* Message history
* User messages
* AI messages
* Markdown rendering
* Code syntax highlighting
* Copy code buttons
* AI thinking/loading animation
* Message input
* Send button
* Logout button
* Responsive mobile interface

---

## ⚡ Frontend → Backend Flow

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
Load chat history
        ↓
Groq AI
        ↓
Generate response
        ↓
Save assistant message
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

## 🏗️ Project Architecture

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
│   ├── ai/
│   │   └── services/
│   │       └── ai_service.py
│   │
│   └── frontend/
│       ├── templates/
│       │   └── frontend/
│       │       ├── base.html
│       │       ├── chat.html
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

## 🛠️ Tech Stack

### Backend

* Python
* Django
* Django REST Framework

### Frontend

* HTML5
* CSS3
* Bootstrap
* JavaScript
* Fetch API
* AJAX
* Django Templates
* Marked
* DOMPurify
* Highlight.js

### Database

* SQLite

### AI

* Groq API
* OpenAI-compatible Python SDK
* GPT-OSS

### Development

* PyCharm Professional
* Git
* GitHub
* Python Virtual Environment

---

## 🔒 Environment Variables

Sensitive data is stored using environment variables.

Create a `.env` file in the root directory:

```env
DJANGO_SECRET_KEY=your-django-secret-key
DEBUG=True

GROQ_API_KEY=your-groq-api-key
AI_MODEL=openai/gpt-oss-120b
```

The real `.env` file must **never be committed to GitHub**.

The repository contains `.env.example` instead:

```env
DJANGO_SECRET_KEY=your-django-secret-key
DEBUG=True

GROQ_API_KEY=your-groq-api-key
AI_MODEL=openai/gpt-oss-120b
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
```

Move into the project:

```bash
cd Personal-Knowledge-AI
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

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

### 5. Apply migrations

```bash
python manage.py migrate
```

---

### 6. Run the application

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## ✅ Current Project Status

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

✅ HTML frontend
✅ CSS styling
✅ Bootstrap
✅ JavaScript
✅ Fetch / AJAX
✅ Login interface
✅ Registration interface
✅ Chat interface
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

## 🗺️ Planned Improvements

The next stages of the project will focus on expanding **Personal Knowledge AI** from an AI chat application into a personal knowledge platform.

### Personal Knowledge & RAG

```text
⬜ Document uploads
⬜ Personal document library
⬜ Document text extraction
⬜ Document chunking
⬜ Embeddings
⬜ Semantic search
⬜ RAG
⬜ Ask questions about documents
⬜ AI-generated answers with sources
```

### Engineering & Production

```text
⬜ Automated tests
⬜ PostgreSQL
⬜ Docker
⬜ Production deployment
```

---

## 🎯 Project Goal

The long-term goal of **Personal Knowledge AI** is to evolve from an AI chat application into a personal knowledge assistant capable of working with a user's own conversations, documents, and knowledge base.

```text
Personal Knowledge AI
        │
        ├── AI Chat
        ├── Chat History
        ├── Personal Library
        ├── Documents
        ├── Semantic Search
        └── RAG
```

---

## 📌 Development Status

The project is currently under active development.

The core AI chat experience is working end-to-end:

```text
Authentication
      ↓
Responsive Frontend
      ↓
REST API
      ↓
Database
      ↓
Conversation Context
      ↓
Groq AI
      ↓
Markdown AI Response
```

The next major development stage is the **personal knowledge layer**, starting with document uploads and a personal document library.

More features will be added incrementally as the project evolves.
