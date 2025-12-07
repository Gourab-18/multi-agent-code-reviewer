# Multi-Agent Code Reviewer

This project is a multi-agent system designed to review code using LangChain, LangGraph, and various other tools.

## Structure

- `src/agents/`: Agent implementations
- `src/tools/`: Code parsing and linting tools
- `src/rag/`: Vector store and retrieval logic (ChromaDB)
- `src/graph/`: LangGraph state machine definitions
- `src/api/`: FastAPI application and endpoints
- `src/models/`: Pydantic data models
- `tests/`: Test suite
- `data/knowledge_base/`: Documentation and best practices for RAG

## Setup

1. Install Poetry if you haven't already.
2. Run `poetry install` to install dependencies.
3. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.

## Usage

(Add usage instructions here)
