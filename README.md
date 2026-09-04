# The Lenny Growth Assistant
> **Enterprise-Grade Conversational AI for Product & Growth Teams Grounded in Lenny’s Podcast Transcripts**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_+_pgvector-4169E1.svg?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black.svg?logo=ollama&logoColor=white)](https://ollama.com/)
[![Tests](https://img.shields.io/badge/Tests-17%20Passed-brightgreen.svg)]()

---

## 1. Executive Summary & Problem Context

Product Managers, Growth Leaders, and Founders frequently need battle-tested frameworks to solve tactical challenges (e.g. paywall positioning, engineering velocity, viral loops, retention curves). Over 200+ hours of tactical wisdom exists in **Lenny’s Podcast**, but this knowledge is trapped in long-form audio and unstructured markdown files.

**The Lenny Growth Assistant** turns this transcript archive into an executive-grade internal intelligence product:
1. **Strictly Grounded Answers:** Delivers source-attributed answers with exact speaker and timestamp citations (`[Episode: Guest Name, Timestamp]`), refusing to answer when evidence is lacking.
2. **Ship 30 for 30 Content Engine:** Encodes the Nicolas Cole & Dickie Bush framework to synthesize grounded knowledge into ~1,250-word, high-retention atomic essays.
3. **Claude-Style Side-by-Side Artifact Viewer:** Natively renders generated Markdown and complete HTML/CSS snippets beside the chat in an isolated container.
4. **Untrusted HTML Sandboxing:** Enforces enterprise security isolation using `<iframe>` containers with `sandbox="allow-scripts"` (strictly omitting `allow-same-origin`) and client-side DOMPurify sanitization.
5. **Dual Model Layer (Local & Cloud):** Allows immediate switching between local LLM execution via Ollama (mandatory for evaluation demo) and Cloud LLMs (Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o) via a 1-click header toggle.

---

## 2. Architecture Overview

```mermaid
graph TD
    Client["Client Browser (React 18 + Vite)"] -->|"HTTP / SSE Streaming"| API["FastAPI Application Tier (:8001)"]
    
    subgraph Application Tier
        API --> Router["Dynamic Provider Router"]
        API --> RAG["RAG & Ingestion Engine"]
        API --> Skills["Skills Engine (Ship 30 for 30)"]
        API --> Parser["Artifact Tag Parser"]
        API --> SessionMgr["PostgreSQL Session Manager"]
    end
    
    subgraph Data & Vector Tier
        RAG -->|"pgvector HNSW Cosine Search"| Postgres[("PostgreSQL 16 + pgvector (:5432)")]
        SessionMgr -->|"CRUD State"| Postgres
    end
    
    subgraph Inference Tier
        Router -->|"Local Driver"| Ollama["Ollama Daemon (:11434, llama3.2:3b)"]
        Router -->|"Cloud Driver"| Claude["Anthropic Claude / OpenAI API"]
    end
    
    subgraph Presentation Sandbox
        Client -->|"Message Stream"| ChatUI["Left Pane: Conversational Chat"]
        Parser -.->|"Artifact Stream"| Viewer["Right Pane: Sandboxed Artifact Drawer"]
        Viewer -->|"sandbox='allow-scripts'"| Iframe["Sandboxed Iframe & DOMPurify"]
    end
```

---

## 3. Quickstart & One-Command Launch

### 3.1 Option A: Docker Compose (Recommended)
Launch the entire multi-service stack (PostgreSQL + pgvector, Ollama, FastAPI Backend, and React Frontend) with a single command:

```bash
# 1. Clone repository and navigate to root
cd d:/Oogway

# 2. Copy environment template
cp .env.example .env

# 3. Start all services
docker-compose up --build
```

Access the services:
- **Frontend Web UI:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend API & Swagger Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **Health Check Probe:** [http://localhost:8001/api/health](http://localhost:8001/api/health)

---

### 3.2 Option B: Local Developer Startup

If you prefer running services directly on your host machine:

#### Prerequisites
- **Python 3.11+** (Python 3.13 tested)
- **Node.js 18+** (Node 24 LTS tested)
- **Docker Desktop** (for PostgreSQL with pgvector)
- **Ollama** (running locally or via Docker)

#### Step 1: Start PostgreSQL with pgvector
```bash
docker run -d --name lenny-postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=lenny_assistant \
  pgvector/pgvector:pg16
```

#### Step 2: Start Ollama and Pull Demo Model
```bash
# Start Ollama container (if not installed natively)
docker run -d --name lenny-ollama -p 11434:11434 ollama/ollama:latest

# Pull the lightweight local demo model (llama3.2:3b)
docker exec lenny-ollama ollama pull llama3.2:3b
```

#### Step 3: Initialize and Ingest Transcripts
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Ingest sample transcripts into pgvector
python backend/scripts/ingest.py --clear
```

#### Step 4: Launch Backend API
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Step 5: Launch Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Environment Variables (`.env.example`)

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant` | Connection string for PostgreSQL with pgvector. |
| `DEFAULT_LLM_PROVIDER` | `ollama` | Active provider (`ollama` for local demo, `cloud` for Claude/OpenAI). |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama daemon endpoint. |
| `OLLAMA_MODEL` | `llama3.2:3b` | Local model weights (`llama3.2:3b`, `llama3.1:8b`, `mistral:7b`). |
| `CLOUD_PROVIDER` | `anthropic` | Cloud provider driver (`anthropic` or `openai`). |
| `ANTHROPIC_API_KEY` | *(optional)* | Anthropic Claude API Key (`claude-3-5-sonnet-20241022`). |
| `OPENAI_API_KEY` | *(optional)* | OpenAI API Key (`gpt-4o-mini`). |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Dense sentence embedding model (384-dimensions). |
| `RETRIEVAL_TOP_K` | `5` | Top-$K$ relevant chunks retrieved per grounded query. |
| `RETRIEVAL_SIMILARITY_THRESHOLD` | `0.35` | Similarity cutoff threshold for anti-hallucination refusal. |

---

## 5. Core Product Capabilities

### 5.1 Grounded Q&A with Verifiable Citations
- Performs HNSW vector similarity search against indexed transcript chunks.
- Inline citation badges `[Episode: Guest Name, Timestamp]` format (e.g., `[Episode: Will Larson, 00:00:00]`).
- Clicking any citation badge opens an expandable card showing the exact excerpt, similarity score, and episode metadata.
- **Anti-Hallucination Gate:** Queries lacking support in Lenny's archive trigger explicit refusal:
  > *"I do not have sufficient information in Lenny's podcast archive to answer this."*

### 5.2 Ship 30 for 30 Content Engine
- Dedicated skill encoding the Nicolas Cole & Dickie Bush framework heuristics:
  - **Hook:** Curiosity gap opening line and high-stakes problem setup.
  - **Progression:** Modular, 1–3 sentence atomic paragraphs.
  - **Skimmable Formatting:** Selective bold anchors at the start of every point.
  - **Takeaway:** Concrete operational framework or checklist.
  - **Word Count:** ~1,250 words, strictly cited from transcript sources.
- Generated essays automatically mount inside the side-by-side artifact viewer.

### 5.3 Claude-Style Sandboxed Artifact Viewer
- Side-by-side drawer renders Markdown and complete HTML/CSS snippets without leaving the chat.
- **Tabs:**
  - **Preview Tab:** Renders rich Markdown or interactive HTML widgets.
  - **Code Tab:** Monospaced source code with line numbers and syntax highlighting.
  - **Copy Action:** 1-click clipboard export.
  - **Download Action:** Exports `.md` or `.html` file.
- **Security Isolation:**
  - HTML rendered inside `<iframe sandbox="allow-scripts">` (strictly NO `allow-same-origin`).
  - Pre-sanitized via `DOMPurify` to eliminate cross-site scripting vectors.

---

## 6. Automated Testing

The backend includes a comprehensive automated test suite with **100% test passing**:

```bash
# Run all automated tests
pytest backend/tests -v
```

### Verified Test Suites:
1. `test_health.py`: Verifies `/api/health` system probes, DB status, and provider telemetry.
2. `test_providers.py`: Tests Ollama, Cloud, and dynamic runtime switching via headers/payload.
3. `test_retrieval.py`: Tests recursive chunking, similarity retrieval, and out-of-domain refusal.
4. `test_skills.py`: Tests Ship 30 for 30 prompt construction and framework heuristics.
5. `test_artifacts.py`: Tests artifact tag extraction, attribute parsing, and chat bubble formatting.
6. `test_sessions.py`: Tests session lifecycle (creation, retrieval, history, deletion).

---

## 7. Operational Resilience & Troubleshooting

| Issue | Root Cause | Automated Resolution |
| :--- | :--- | :--- |
| **Ollama Daemon Unreachable** | Ollama container stopped or not listening on port 11434. | The UI displays an offline badge; the chat endpoint yields a helpful message suggesting starting Ollama rather than crashing. |
| **Model Weights Missing** | Configured model (`llama3.2:3b`) not pulled into Ollama. | Health probe identifies model readiness; returns clear instructions to run `ollama pull llama3.2:3b`. |
| **PostgreSQL Disconnected** | DB container initializing. | Connection pre-pinging with automatic retry; unit tests automatically utilize isolated SQLite fallback mode. |
| **Out-of-Domain Prompt** | User asks off-topic question (e.g. cooking recipe). | Retrieval threshold refuses prompt without wasting tokens or hallucinating. |

---

## 8. Forward Deployment Handoff & Extensions

To extend this solution for new client engagements:
1. **Adding New Episodes:** Place new transcript markdown files in `backend/data/sample_transcripts/` or point `ingest.py` to a cloned repo:
   ```bash
   python backend/scripts/ingest.py --source /path/to/transcripts
   ```
2. **Adding a New Agent Skill:** Create a new skill prompt in `backend/app/skills/` and expose it via a route in `backend/app/api/skills.py`.
3. **Connecting Enterprise Auth:** Integrate OAuth2 / SAML middleware into `backend/app/main.py` and bind user IDs to `SessionModel.user_id`.
