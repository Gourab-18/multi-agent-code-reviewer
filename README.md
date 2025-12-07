<img width="739" height="398" alt="Screenshot 2025-12-07 at 5 20 22 PM" src="https://github.com/user-attachments/assets/67c04633-4907-40ce-9951-0aa0d1960250" />
<img width="742" height="401" alt="Screenshot 2025-12-07 at 5 20 11 PM" src="https://github.com/user-attachments/assets/d11441c8-f27a-479d-aacf-f078545fd0da" />
<img width="1468" height="725" alt="Screenshot 2025-12-07 at 5 19 29 PM" src="https://github.com/user-attachments/assets/74ef833a-191d-4ce2-9b7b-3583236c8e65" />
<img width="738" height="400" alt="Screenshot 2025-12-07 at 5 19 17 PM" src="https://github.com/user-attachments/assets/c678db4f-8e0b-4750-9f65-b310d4ec7678" />
# Multi-Agent Code Reviewer

An intelligent, full-stack code review assistant powered by LLMs (OpenAI/Groq), LangGraph, and RAG. It employs multiple specialized agents to analyze code for security, performance, and quality issues, resolving conflicts to provide a unified, actionable report.

## 🏗️ Architecture

The system follows a micro-service inspired modular architecture where the Frontend acts as a client to the FastAPI backend, which orchestrates the multi-agent workflow.

```mermaid
graph TD
    User[User / Developer] -->|Drag & Drop Code| FE[React Frontend]
    FE -->|POST /api/review| API[FastAPI Backend]
    API -->|Invoke| Workflow[LangGraph Workflow]
    
    subgraph "Retrieval Augmented Generation (RAG)"
        KB[(ChromaDB Knowledge Base)]
        Docs[Coding Guidelines] -->|Index| KB
    end

    subgraph "Review Agents (Parallel Execution)"
        Workflow -->|Parse & Analyze| SA[Security Agent]
        Workflow -->|Parse & Analyze| PA[Performance Agent]
        Workflow -->|Parse & Analyze| QA[Quality Agent]

        KB -.->|Retrieve Context| SA
        KB -.->|Retrieve Context| PA
        KB -.->|Retrieve Context| QA
    end
    
    subgraph "Consolidation"
        SA & PA & QA -->|Findings| OA[Orchestrator Agent]
        OA -->|De-duplicate & Merge| Final[Final Review Report]
    end

    Final -->|JSON| API
    API -->|Render Report| FE
```

## 🧩 Components

### 1. **Core Agents**
-   **Security Agent**: Focuses on vulnerabilities (SQLi, XSS, Secrets). Uses `bandit`-like logic and LLM reasoning.
-   **Performance Agent**: Identifies O(N^2) loops, resource leaks, and inefficient logic.
-   **Quality Agent**: Checks naming conventions, modularity, and code style.
-   **Orchestrator**: The "Team Lead" that merges findings, removes duplicates, and generates the executive summary.

### 2. **RAG Engine**
-   Uses **ChromaDB** to store coding guidelines and best practices.
-   Agents retrieve relevant documents (e.g., "OWASP Top 10" or "Python Optimization Tips") to ground their reviews.

### 3. **Tech Stack**
-   **Frontend**: React, Vite, Tailwind CSS (Dark Mode), Lucide Icons.
-   **Backend**: Python, FastAPI, Pydantic.
-   **AI Orchestration**: LangChain, LangGraph.
-   **LLM Support**: OpenAI (GPT-3.5/4) or Groq (Llama 3).

---

## 🚀 Getting Started

### Prerequisites
-   Python 3.9+
-   Node.js 18+
-   OpenAI API Key OR Groq API Key

### 1. Backend Setup
```bash
# Clone repository
git clone <repo-url>
cd multi-agent-code-reviewer

# Install Python dependencies
pip install -r requirements.txt
# OR if using poetry
poetry install

# Configure Environment
cp .env.example .env
# Edit .env and add your API keys (OPENAI_API_KEY or GROQ_API_KEY)
```

Run the server:
```bash
# Start FastAPI (Reload mode)
python3 -m uvicorn src.api.main:app --reload
```
API runs at: `http://127.0.0.1:8000`

### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Dev Server
npm run dev
```
Frontend runs at: `http://localhost:5173`

## 🛠️ Configuration (LLM Provider)
You can switch between OpenAI and Groq by changing the `.env` file:
```bash
# Options: openai, groq, ollama
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
```
Restart the backend after changing the provider.

## 📂 Folder Structure
-   `src/agents/`: Logic for individual agents.
-   `src/graph/`: LangGraph workflow definition.
-   `src/api/`: REST API endpoints.
-   `frontend/`: React application.
-   `data/knowledge_base/`: Markdown files for RAG.
