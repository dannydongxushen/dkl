# ClinicPilot AI: Technical Design Document

## 1. Architectural Choices

The goal of this project is to build a robust, end-to-end MVP for an intelligent clinic assistant. Rather than using heavy abstraction frameworks (like LangChain or LlamaIndex), I chose a **lightweight custom orchestration architecture** powered by **FastAPI**, **OpenAI-compatible SDK (DeepSeek)**, and **native Python**.

**Why avoid heavy frameworks?**
- **Transparency & Control**: A custom Agent loop provides full visibility into the state, tool executions, and prompt injection, which is critical for debugging and ensuring reliable medical outputs.
- **Lower Latency**: Bypassing LangChain's overhead reduces response time.
- **Easier Extensibility**: Integrating MCP (Model Context Protocol) or custom REST APIs is straightforward without fighting framework-specific abstractions.

## 2. Data Layer Design (SQLite vs. ChromaDB)

The system adopts a **polyglot persistence** approach, separating structured transactional data from unstructured semantic knowledge.

- **SQLite (Relational)**: Used for high-integrity business operations (bookings, patient profiles). The Agent explicitly executes SQL `INSERT` and `SELECT` queries via tools, ensuring strict transactional boundaries.
- **ChromaDB (Vector Store)**: Used for RAG. 
  - *Chunking Strategy*: Rather than naive fixed-length chunking, the data is dynamically flattened by entity. For example, an entire doctor row (`Doctor ID`, `Name`, `Specialty`, `Bio`) is concatenated into a single natural language sentence. This ensures each vector represents a complete, semantically rich entity.

## 3. AI Agent & Intent Recognition Workflow

The core intelligence is powered by **DeepSeek** (via an OpenAI-compatible API). Intent routing is achieved implicitly through **Function Calling (Tool Calling)**.

- **Q&A / Recommendation Intent** -> Invokes `search_clinical_knowledge` (Triggers RAG).
- **Existing Booking Queries** -> Invokes `get_patient_bookings` (Queries SQLite).
- **New Booking Intent** -> Invokes `create_booking` (Writes to SQLite).

**Conversational Parameter Extraction**: When booking, the Agent must collect `doctor_id`, `treatment_id`, `date`, and `time`. The tool schema enforces these as `required`. If the user provides partial information, the LLM naturally prompts the user to supply the missing parameters rather than hallucinating.

## 4. Deep Dive: RAG Pipeline (Embedding & Reranker)

To ensure high accuracy in medical recommendations, the RAG engine utilizes a **Two-Stage Retrieval (Recall + Re-rank)** architecture. 

### 4.1 Embedding Model Selection & Implementation
- **Model**: `Qwen/Qwen3-Embedding-0.6B` (1024 dimensions).
- **Why Qwen3 over lightweight models (e.g., `all-MiniLM-L6-v2`)?** 
  - MiniLM (384 dims) is extremely fast but struggles with complex medical terminology and multi-lingual semantic matching. 
  - Qwen3-Embedding provides vastly superior semantic precision (ranked top on MTEB benchmarks). Since our dataset is small (only 11 chunks), the trade-off of slightly higher CPU inference time is completely acceptable for the massive gain in retrieval accuracy.
- **Implementation Details**: 
  - We use `sentence-transformers` to load the model locally in FP32 (`torch.float32`) to ensure numerical stability on CPUs.
  - The text is encoded with `normalize_embeddings=True` to ensure cosine similarity calculations are mathematically correct.
  - **ID Injection**: Because the LLM needs `doctor_id` and `treatment_id` to trigger the booking tool, the textual representation fed into the embedding model explicitly includes these IDs (e.g., `"Doctor ID: D101. Doctor Name: Dr. Sarah Jenkins..."`), ensuring the ID is retrieved during RAG.

### 4.2 Reranker (Cross-Encoder) Implementation
- **Model**: `Qwen/Qwen3-Reranker-0.6B`.
- **Why a Reranker?** Vector databases use Bi-Encoders (embedding queries and documents separately), which can retrieve semantically similar but contextually irrelevant documents. A Cross-Encoder (Reranker) processes the query and document *together*, capturing deep contextual interactions.
- **Two-Stage Flow**: 
  1. ChromaDB performs a fast dense retrieval to fetch the **Top-5** candidates.
  2. The Reranker scores these 5 candidates against the user query, and we truncate the list to the **Top-2** most relevant contexts. This drastically reduces prompt tokens and eliminates noise for the LLM.

## 5. Observability & Robustness

- **Full-Link Tracing**: The system implements a dual-track observability strategy. It logs LLM token usage and latency to a local JSONL file. If Litefuse (an OpenTelemetry-compatible local tracing service) is active on port 23100, it pushes Span trees (ChromaDB -> Reranker -> LLM) for visualization.
- **Graceful Degradation**: If the LLM API times out or Litefuse is unreachable, the system logs the error and falls back gracefully without crashing the FastAPI server.
- **Static File Serving**: FastAPI serves both the `/api` routes and the static frontend UI, eliminating CORS issues and simplifying deployment.

## 6. Future Improvements (Production Readiness)
- **MCP Integration**: The `execute_tool` function can be swapped to use Model Context Protocol (MCP) for standardized tool discovery.
- **Containerization**: Wrap the FastAPI app and Litefuse into a `docker-compose` environment.
- **Hybrid Search**: Introduce BM25 keyword search alongside vector search to handle exact ID lookups more reliably.