# Agent Coding Transcripts & Engineering Decision Log
## The Lenny Growth Assistant

**Engagement:** Forward Deployed Engineer Assignment  
**Agent Workspace:** `d:/Oogway`  
**Recording Date:** 2026-09-04  

---

## 1. Initial Assessment & Discovery Phase

### 1.1 Discovery Findings
- **Repository State:** Clean workspace initialized on Windows environment.
- **Local Runtimes:** Python 3.13 / 3.14, Node v24.11.0, Docker Desktop v29.6.1.
- **Transcript Repository Analysis:** Inspected `https://github.com/ChatPRD/lennys-podcast-transcripts`. Confirmed YAML frontmatter schema (`guest`, `title`, `youtube_url`, `publish_date`, `keywords`) and speaker-timestamp structure (`Speaker (HH:MM:SS):`).

### 1.2 Architectural Decisions
1. **Embedding Model Choice:**
   - Evaluated Ollama embedding vs. `sentence-transformers/all-MiniLM-L6-v2`.
   - *Decision:* Standardized on `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) for zero-latency local embedding, deterministic batch processing, and exact cosine similarity alignment with pgvector.
2. **Dual-Model Routing Layer:**
   - Evaluated hardcoding Ollama vs. flexible factory.
   - *Decision:* Implemented `LLMProviderInterface` with dynamic switching via header (`X-LLM-Provider`) or payload (`provider`), enabling instant frontend model toggling and resilient fallback.
3. **Artifact Security Isolation:**
   - Evaluated raw HTML injection vs. iframe sandboxing.
   - *Decision:* Implemented isolated `<iframe>` with `sandbox="allow-scripts"` and strictly NO `allow-same-origin`, combined with `DOMPurify` HTML pre-sanitization.

---

## 2. Iteration Log & Correction Trajectory

### Attempt 1: Winget Package Verification
- **Action:** Attempted interactive winget search for Ollama (`winget list ollama`).
- **Failure Mode:** Winget stalled requesting interactive agreement to Microsoft Store terms of transaction.
- **Correction:** Terminated interactive task immediately; pulled official Docker images (`pgvector/pgvector:pg16` and `ollama/ollama:latest`) and configured native HTTP client connectors.

### Attempt 2: Dual-Driver Database Architecture (PostgreSQL pgvector + SQLite fallback)
- **Challenge:** Evaluators running unit tests on machines without Docker running might face failed test runs if PostgreSQL connection fails.
- **Solution:** Implemented SQLAlchemy session factory with automatic fallback support for SQLite during standalone test runs, while defaulting to PostgreSQL 16 + pgvector in Docker.

### Attempt 3: Ship 30 for 30 Prompt Heuristics Tuning
- **Challenge:** Initial prompts resulted in generic PM summaries rather than the distinct Nicolas Cole / Dickie Bush atomic essay format.
- **Solution:** Encoded strict formatting rules in `Ship30Skill`:
  - Hook formulas: Outcome promise, curiosity gap, or counterintuitive thesis.
  - Sentence length: 1–3 sentence atomic paragraphs.
  - Skimmable formatting: Bold lead-in phrases for every paragraph.
  - Concrete framework: Actionable takeaway checklist.
  - Length: ~1,250 words.

### Attempt 4: Claude-Style Side-by-Side Artifact Drawer
- **Challenge:** Parsing streaming artifact tags in real-time without broken DOM states.
- **Solution:** Implemented robust regex-based tag extractor in `backend/app/artifacts/parser.py` that buffers incoming tokens, extracts `<artifact type="..." title="..." identifier="...">...</artifact>` blocks, and emits them over dedicated SSE events.

---

## 3. Secret Sanitization Confirmation
- No production secrets, API keys, or private tokens are recorded in transcripts or committed files.
- `.env.example` provides placeholders only (`ANTHROPIC_API_KEY=`, `OPENAI_API_KEY=`).
