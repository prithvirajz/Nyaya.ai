# NyayaAI – AI Legal Assistant for Indian Citizens

<p align="center">
  <strong>🇮🇳 A multilingual (English + Hindi) AI legal assistant that explains Indian laws in simple language using RAG and LLMs.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/FAISS-3B82F6?style=for-the-badge" />
  <img src="https://img.shields.io/badge/OpenRouter-FF6B35?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
</p>

---

## 🎯 Problem Statement

Indian citizens often struggle to understand their legal rights due to:
- Complex legal language
- Expensive legal consultations
- Limited access to legal resources in regional languages

**NyayaAI** bridges this gap by providing an AI-powered legal assistant that:
- Explains Indian laws in **simple language** (Hindi & English)
- Answers legal questions with **relevant law citations**
- Provides **actionable next steps**
- Uses **Retrieval-Augmented Generation (RAG)** for accurate, grounded responses

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   React UI   │────▶│   FastAPI    │────▶│   OpenRouter     │
│  (Vite +     │     │   Backend    │     │   LLM (Mistral)  │
│  Tailwind)   │◀────│              │◀────│                  │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                           │
                    ┌──────▼───────┐
                    │  FAISS Index │
                    │  (Embeddings │
                    │  + Metadata) │
                    └──────────────┘
```

**RAG Pipeline:** PDF → Clean → Chunk → Embed (MiniLM) → FAISS → Retrieve → LLM → Structured Response

> See [architecture.md](./architecture.md) for a detailed breakdown.

---

## 🛠️ Tech Stack

| Layer        | Technology                              |
| ------------ | --------------------------------------- |
| Frontend     | React 18, Vite, Tailwind CSS            |
| Backend      | FastAPI, Python 3.11+                   |
| LLM          | OpenRouter API (Mistral 7B Instruct)    |
| Embeddings   | sentence-transformers (all-MiniLM-L6-v2)|
| Vector Store | FAISS (local, free)                     |
| Deployment   | Vercel (frontend) + Render (backend)    |

---

## 📁 Project Structure

```
Nyaya.ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with /ask, /health, /feedback
│   │   ├── config.py            # Centralised settings (pydantic-settings)
│   │   ├── rag/
│   │   │   ├── ingest.py        # PDF → chunks → FAISS pipeline
│   │   │   ├── retriever.py     # Similarity search over FAISS
│   │   │   └── prompts.py       # System prompt & bilingual templates
│   │   ├── services/
│   │   │   ├── llm_service.py   # Async OpenRouter LLM client
│   │   │   └── embedding_service.py  # Sentence-transformer singleton
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   └── utils/
│   │       └── security.py      # Input sanitisation & injection detection
│   ├── data/
│   │   └── pdfs/                # Place legal PDFs here
│   ├── evaluate.py              # Evaluation with 10 test questions
│   ├── render.yaml              # Render deployment blueprint
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main chat interface
│   │   ├── api/client.js        # API client
│   │   └── components/
│   │       ├── Header.jsx       # Logo + language toggle
│   │       ├── ChatInput.jsx    # Auto-resizing input
│   │       ├── ChatMessage.jsx  # Structured response cards
│   │       └── Disclaimer.jsx   # Legal disclaimer
│   ├── vercel.json              # Vercel deployment config
│   └── package.json
├── README.md
└── architecture.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- An [OpenRouter](https://openrouter.ai/) API key (free tier available)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       
# source venv/bin/activate   

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Add legal PDF to data/pdfs/ (follow naming convention in data/pdfs/README.md)

# Run ingestion pipeline
python -m app.rag.ingest

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies to localhost:8000)
npm run dev
```

Visit **http://localhost:5173** to use the app.

---

## 🌐 Deployment

### Backend → Render (Free Tier)

1. Push code to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/).
3. Click **New → Web Service** → connect your repo.
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `OPENROUTER_API_KEY`.
6. Deploy.

### Frontend → Vercel (Free Tier)

1. Go to [Vercel Dashboard](https://vercel.com/).
2. Import your GitHub repo → select `frontend/` as root.
3. Set environment variable: `VITE_API_URL=https://your-render-url.onrender.com`.
4. Deploy.

---

## 📊 Evaluation

```bash
cd backend
python evaluate.py
```

Runs 10 diverse legal questions through the RAG pipeline and prints retrieved chunks + LLM responses with timing metrics.

---

## 🔐 Security Features

- **Input sanitisation** – strips prompt-injection patterns and control characters
- **Query length validation** – enforces min/max character limits
- **Rate limiting** – 10 requests/minute per IP (configurable)
- **CORS** – configurable allowed origins
- **No hardcoded secrets** – all via environment variables

---

## 📝 Resume Bullet Points

> - Built **NyayaAI**, a production-grade, multilingual (Hindi + English) AI legal assistant using **RAG architecture** with **FAISS** vector search, **FastAPI**, and **OpenRouter LLM (Mistral 7B)**
> - Engineered a complete **PDF ingestion pipeline** that processes Indian legal documents (IPC, CrPC, Consumer Protection Act) with text cleaning, chunking, and metadata extraction
> - Designed **structured prompt engineering** with bilingual system prompts producing JSON-formatted legal guidance with law citations, rights, next steps, and mandatory disclaimers
> - Implemented **security best-practices** including input sanitisation, prompt-injection detection, rate limiting, and query validation
> - Developed a **responsive React frontend** (Vite + Tailwind CSS) with glassmorphism design, real-time chat interface, Hindi/English toggle, and clipboard-copy functionality
> - Deployed backend on **Render** and frontend on **Vercel** with CI/CD, achieving sub-2s retrieval latency on free-tier infrastructure

---

## 📜 License

This project is open-source for educational and portfolio purposes.

---

<p align="center">
  Made with ❤️ for Indian Citizens 🇮🇳
</p>
