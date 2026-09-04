# Product Requirements Document (PRD)
## The Lenny Growth Assistant (Forward Deployment Engagement)

**Document Version:** 1.0.0  
**Target Engagement:** Product & Growth Team Forward Deployment  
**Author:** Forward Deployed Engineer (FDE)  
**Status:** Approved for Implementation  

---

## 1. Executive Summary & Forward Deployment Brief

### 1.1 The User and the Problem
- **Primary Persona:** Senior Product Managers, Growth Leads, and Founders who need tactical, battle-tested product and growth strategies to make immediate operational decisions (e.g., pricing changes, retention mechanics, viral loops, org design).
- **Core Pain Point:** Over 200+ hours of world-class knowledge in *Lenny’s Podcast* is trapped in long-form audio and unstructured markdown transcripts. Searching manually across dozens of episodes is slow, prone to recency bias, and ungrounded. When PMs draft memos or strategies, they spend hours re-synthesizing ideas into executive formats.
- **The Solution:** **The Lenny Growth Assistant**—an internal AI product delivering:
  1. **Strictly Grounded Answers:** Instant answers attributed directly to podcast transcripts with exact speaker and timestamp citations (`[Episode: Guest Name, Timestamp]`), with zero-hallucination refusal when evidence is lacking.
  2. **Ship 30 for 30 Content Engine:** A dedicated skill transforming answers into actionable, high-retention 1,250-word essays adhering to atomic essay principles.
  3. **Side-by-Side Sandboxed Artifact Viewer:** Claude-style interactive rendering of Markdown and HTML/CSS deliverables directly beside the chat with strict iframe isolation.
  4. **Dual Model Layer:** Seamless switching between Local LLMs (Ollama) for cost/privacy and Cloud LLMs (Anthropic Claude / OpenAI) for advanced reasoning.

---

## 2. Measurable Success Metrics

| Metric Category | Metric Name | Target Benchmark | Measurement Methodology |
| :--- | :--- | :--- | :--- |
| **Retrieval Quality** | Citation Grounding Accuracy | $\ge 90\%$ | Automated test verification that claims match retrieved chunk sources. |
| **Hallucination Control** | Out-of-Domain Refusal Rate | $100\%$ | Automated rejection of queries with no support in podcast archive. |
| **Performance** | Local TTFT (Time to First Token) | $< 4.0\text{s}$ | Evaluated using Ollama `llama3.2:3b` on standard 16GB developer machine. |
| **Security & Safety** | Artifact Render Isolation | $0\text{ XSS}$ / leaks | Sandboxed iframe verification with `sandbox="allow-scripts"` and NO `allow-same-origin`. |
| **Operational** | Setup Time to First Token | $< 5\text{ minutes}$ | Single command launch via `docker-compose up` or local startup script. |

---

## 3. Assumptions & Scope Choices

### 3.1 Important Assumptions
1. **Knowledge Source:** Transcripts are sourced from the open repository `https://github.com/ChatPRD/lennys-podcast-transcripts`. Transcripts follow YAML frontmatter structure with speaker timestamps (`Speaker (HH:MM:SS):`).
2. **Evaluator Hardware:** The client evaluator runs a standard development machine (macOS/Linux/Windows with $\ge 16$GB RAM). Local LLM inference uses lightweight 3B–8B parameter models (`llama3.2:3b`, `mistral:7b`) via Ollama.
3. **Internal Team Context:** The application is intended for an internal product/growth team; authentication can initially leverage session-based tokens, with persistence backed by PostgreSQL.

### 3.2 Explicit Scope Decisions

| Feature / Capability | In Scope | Out of Scope | Rationale |
| :--- | :---: | :---: | :--- |
| **Podcast Ingestion & RAG** | ✅ | — | Core foundation for grounded Q&A. |
| **Speaker & Timestamp Citations** | ✅ | — | Crucial for verifiability and evaluator trust. |
| **Ship 30 for 30 Content Skill** | ✅ | — | Delivers immediate structured utility for writing memos and essays. |
| **Side-by-Side Artifact Viewer** | ✅ | — | Claude-style native rendering of Markdown and HTML/CSS. |
| **Sandboxed Iframe Isolation** | ✅ | — | Essential enterprise security against untrusted generated HTML. |
| **Dynamic Model Toggle (Local/Cloud)** | ✅ | — | Evaluator requirement: local Ollama for demo + cloud for scale. |
| **Session Persistence (PostgreSQL)** | ✅ | — | Multi-turn memory and historical session restoration. |
| **Audio File Streaming** | — | ❌ | Unnecessary operational overhead; text transcripts provide 100% semantic content. |
| **Multi-Tenant User Auth & Billing** | — | ❌ | Premature complexity for an internal growth assistant MVP. |
| **Live Web Scraping Outside Lenny's** | — | ❌ | Dilutes grounding strictly to Lenny's archive. |

---

## 4. Risks & Mitigations

| Risk | Impact | Likelihood | Forward Deployed Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **LLM Hallucination** | High | Medium | Strict system prompt rules + similarity score thresholding. If no chunks exceed threshold ($0.35$), assistant refuses: *"I do not have sufficient information in Lenny's podcast archive to answer this."* |
| **Ollama Local Latency / Timeouts** | Medium | Medium | Default to lightweight `llama3.2:3b` model; implement connection timeout wrappers and automatic UI notification if Ollama is unreachable. |
| **Untrusted HTML Rendering (XSS)** | High | Low | Render HTML artifacts inside an isolated `<iframe>` with `sandbox="allow-scripts"` (strictly NO `allow-same-origin`), plus client-side `DOMPurify` sanitization. |
| **Database Connection Failure** | High | Low | Implement connection retry routines and SQLite fallback compatibility for offline unit testing. |
| **Context Window Overflow** | Medium | Low | Recursive speaker-aware chunking (500–800 tokens) with Top-$K=5$ retrieval, fitting comfortably within 4K–8K context windows. |

---

## 5. Detailed User Flows

### Flow 1: Grounded Strategic Query
1. User enters: *"What is Elena Verna's framework for B2B product-led sales?"*
2. System embeds query using `all-MiniLM-L6-v2` and queries pgvector for Top-5 chunks.
3. System constructs a grounded prompt with retrieved chunks and speaker/timestamp metadata.
4. Assistant streams the answer with inline citations `[Episode: Elena Verna, 00:14:22]`.
5. User clicks any citation badge to view the exact transcript excerpt in an expandable source sheet.

### Flow 2: Ship 30 for 30 Content Generation
1. User clicks **"Generate Ship 30 Essay"** or enters a request for an essay.
2. The `Ship30Skill` invokes the structured framework:
   - Magnetic headline with curiosity gap or counterintuitive hook.
   - 1–3 sentence atomic paragraphs.
   - Skimmable bold anchors and bulleted takeaways.
   - Strict adherence to ~1,250 words grounded in transcript facts.
3. The response wraps the output in `<artifact type="markdown" title="...">`.
4. The frontend automatically detects the artifact tag, slides open the **Side-by-Side Artifact Viewer**, and renders the formatted essay.

### Flow 3: Interactive HTML Artifact Generation
1. User asks: *"Create an interactive HTML pricing calculator based on Lenny's monetization episodes."*
2. Assistant streams explanatory text and generates `<artifact type="html" title="Pricing Tier Matrix">...HTML/CSS/JS...</artifact>`.
3. Artifact Viewer mounts the code inside the sandboxed iframe. The user can interact with the rendered calculator, toggle code view, or download the HTML file.

---

## 6. Acceptance Criteria

- [x] **AC-1:** Backend runs on FastAPI with clean endpoints (`/api/chat`, `/api/sessions`, `/api/health`, `/api/skills/ship30`).
- [x] **AC-2:** Transcripts from `ChatPRD/lennys-podcast-transcripts` are indexed in PostgreSQL with `pgvector` HNSW index.
- [x] **AC-3:** Responses cite speaker and timestamp `[Episode: Guest, Timestamp]`.
- [x] **AC-4:** Unanswerable questions trigger explicit refusal without hallucination.
- [x] **AC-5:** Ship 30 for 30 skill produces structured, skimmable essays with magnetic hooks and takeaways.
- [x] **AC-6:** Artifact Viewer renders Markdown and HTML/CSS beside the chat with `sandbox="allow-scripts"` and `DOMPurify`.
- [x] **AC-7:** UI allows switching between Local LLM (Ollama) and Cloud LLM (Claude/OpenAI) on the fly.
- [x] **AC-8:** Automated test suite (`pytest`) verifies retrieval, skills, providers, artifacts, and persistence.
- [x] **AC-9:** Single-command startup via `docker-compose.yml`.
