Here is the complete `README.md` file. You can directly copy and paste this into your `recrulink/README.md` file.

```markdown
# RecruLink – RAG-Based Resume Matching System

An end-to-end AI application that uses **Retrieval-Augmented Generation (RAG)**, **FAISS vector search**, **BAAI/bge-m3 embeddings**, and **Gemini 2.5 Flash** to semantically match resumes against job descriptions and generate AI-powered candidate analysis and interview questions.

---

## Architecture

```text
┌──────────────┐     ┌───────────────┐     ┌─────────┐
│   Angular    │────▶│   FastAPI     │────▶│  MySQL  │
│   Frontend   │     │   Backend     │     │         │
└──────────────┘     │               │     └─────────┘
                     │  ┌─────────┐  │
                     │  │  FAISS  │  │     ┌─────────┐
                     │  │  Index  │  │────▶│ Gemini  │
                     │  └─────────┘  │     │ 2.5Flsh │
                     └───────────────┘     └─────────┘
```

### RAG Pipeline Flow

1. User uploads resumes (PDF/DOCX) → text is extracted
2. Text is split into overlapping chunks (500 chars, 100 overlap)
3. Each chunk is embedded using **BAAI/bge-m3** (1024-dim vectors)
4. Embeddings are stored in a **FAISS** IndexFlatIP (cosine similarity)
5. Chunk metadata is stored in **MySQL** (candidate_id, chunk_text, faiss_index_id)
6. User submits a job description → embedded with bge-m3
7. FAISS retrieves top-k similar chunks → grouped by candidate
8. Ranked candidates are sent to **Gemini 2.5 Flash** for analysis
9. AI generates: match score, skills assessment, recommendation, interview questions

---

## Quick Start (Docker Compose)

### Prerequisites

- Docker and Docker Compose installed
- A Google Gemini API key

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manojkumar4646/recrulink.git
   cd recrulink
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your `GEMINI_API_KEY`.

3. **Build and run:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8.0+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your MySQL credentials and Gemini API key

# Create MySQL database
mysql -u root -p -e "CREATE DATABASE recrulink;"

# Run the server
python run.py
# Or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
# Opens at http://localhost:4200
```

> **Note:** For local development, update `frontend/src/environments/environment.ts` to point to your local backend: `apiUrl: 'http://localhost:8000/api'`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-resumes` | Upload PDF/DOCX resumes |
| POST | `/api/submit-job` | Store a job description |
| POST | `/api/match-candidates` | Match candidates against JD |
| GET | `/api/candidate/{id}` | Get candidate details |
| POST | `/api/generate-analysis` | Generate AI analysis |
| POST | `/api/generate-questions` | Generate interview questions |
| GET | `/api/candidates` | List all candidates |
| DELETE | `/api/clear` | Clear all data and reset FAISS |
| GET | `/api/health` | Health check |

---

## Sample Job Description (for testing)

```text
Senior Software Engineer - AI/ML Platform

We are seeking a Senior Software Engineer to build and maintain our
AI/ML platform. The ideal candidate has:

Required Skills:
- Python programming (5+ years)
- Machine Learning and Deep Learning frameworks (PyTorch, TensorFlow)
- Natural Language Processing (NLP) experience
- Experience with LLMs and RAG systems
- Cloud platforms (AWS, GCP, or Azure)
- Docker and Kubernetes
- CI/CD pipelines and MLOps practices

Responsibilities:
- Design and build scalable ML pipelines
- Implement RAG-based retrieval systems
- Optimize model inference for production
- Mentor junior engineers

Qualifications:
- Bachelor's or Master's in Computer Science or related field
- 5+ years of software development experience
- 3+ years of ML/AI experience
- Strong problem-solving and communication skills
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Angular 17, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Pydantic |
| Embeddings | BAAI/bge-m3 (1024-dim) via sentence-transformers |
| Vector Store | FAISS (IndexFlatIP, cosine similarity) |
| LLM | Google Gemini 2.5 Flash |
| Database | MySQL 8.0 via SQLAlchemy / PyMySQL |
| Text Splitting | LangChain RecursiveCharacterTextSplitter |
| PDF Extraction | PyMuPDF (fitz) |
| DOCX Extraction | python-docx |
| Containers | Docker, Docker Compose |

---

## Database Schema

### `candidates`
| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| name | VARCHAR(255) | Extracted candidate name |
| email | VARCHAR(255) | Extracted email |
| phone | VARCHAR(50) | Extracted phone |
| file_name | VARCHAR(500) | Original filename |
| uploaded_at | DATETIME | Upload timestamp |

### `resume_chunks`
| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| candidate_id | INT FK | Reference to candidates.id |
| chunk_text | TEXT | Chunk text content |
| faiss_index_id | INT | Position in FAISS index |

### `job_descriptions`
| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| description | TEXT | Job description text |
| created_at | DATETIME | Submission timestamp |

---

## Environment Variables

### Root `.env` (Used by Docker Compose)
```env
GEMINI_API_KEY=your_gemini_api_key_here
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=recrulink
MYSQL_USER=recrulink
MYSQL_PASSWORD=rootpassword
```

### Backend `backend/.env` (Used for local development)
```env
GEMINI_API_KEY=your_gemini_api_key_here
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=recrulink
MYSQL_USER=root
MYSQL_PASSWORD=rootpassword
FAISS_INDEX_PATH=faiss_index
```

---

## Key Design Decisions

1. **BAAI/bge-m3 over OpenAI**: Free, local, multilingual embedding model.
2. **FAISS IndexFlatIP**: Exact search with inner product on normalized vectors = cosine similarity.
3. **Singleton EmbeddingService**: Model loaded once (~2.2GB VRAM/RAM), shared across all requests.
4. **Chunk-based retrieval**: Better semantic coverage than whole-document embedding.
5. **Weighted scoring**: 60% best chunk score + 40% average score for candidate ranking.
6. **Gemini 2.5 Flash**: Fast, cost-effective LLM with structured JSON output parsing.

---

## Project Structure

```text
recrulink/
├── backend/
│   ├── main.py                # FastAPI app entry point
│   ├── run.py                 # Startup script (waits for MySQL)
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile
│   ├── api/
│   │   ├── routes.py          # API endpoint definitions
│   │   └── models.py          # Pydantic request/response models
│   ├── services/
│   │   ├── text_extractor.py  # PDF/DOCX text extraction
│   │   ├── chunk_service.py   # LangChain text chunking
│   │   ├── gemini_service.py  # Gemini LLM integration
│   │   └── resume_service.py  # Resume processing orchestrator
│   ├── rag/
│   │   ├── faiss_store.py     # FAISS index management
│   │   └── pipeline.py        # RAG retrieval pipeline
│   ├── embeddings/
│   │   └── embedding_service.py  # BAAI/bge-m3 wrapper
│   └── database/
│       ├── connection.py      # SQLAlchemy engine & session
│       └── models.py          # ORM table definitions
├── frontend/
│   ├── src/app/
│   │   ├── app.component.ts   # Main app layout & logic
│   │   ├── components/
│   │   │   ├── resume-upload/ # Drag-and-drop upload
│   │   │   ├── job-description/ # JD text input
│   │   │   ├── results/       # Match results & analysis
│   │   │   ├── loading-spinner/ # Loading indicator
│   │   │   └── toast/         # Toast notifications
│   │   ├── services/
│   │   │   ├── api.service.ts # HTTP client
│   │   │   └── toast.service.ts # Toast notification service
│   │   └── models/            # TypeScript interfaces
│   ├── Dockerfile
│   └── nginx.conf             # Nginx config with API proxy
├── docker-compose.yml
└── README.md
