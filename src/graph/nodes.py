from typing import List, Dict, Any, Optional
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

from src.models.schemas import GraphState, CodeFile, AgentReview, ReviewFinding, FinalReview, ConflictResolution
from src.tools.code_parser import CodeParser
from src.rag.knowledge_base import KnowledgeBaseRetriever
from src.rag.codebase_indexer import CodebaseRetriever

# Agents
from src.agents.security_agent import SecurityAgent
from src.agents.performance_agent import PerformanceAgent
from src.agents.quality_agent import CodeQualityAgent
from src.agents.orchestrator import OrchestratorAgent

# Initialize shared resources (can be optionally dependency injected)
provider = os.getenv("LLM_PROVIDER", "openai").lower()
print(f"Initializing LLM with provider: {provider}")

if provider == "groq" and ChatGroq:
    # Requires GROQ_API_KEY env var
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
elif provider == "ollama" and ChatOllama:
    # Requires local Ollama running
    llm = ChatOllama(model="llama3", temperature=0)
else:
    # Default to OpenAI
    if provider != "openai":
        print(f"Warning: Provider '{provider}' not available or installed. Fallback to OpenAI.")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

orchestrator_agent = OrchestratorAgent(llm)

# Try initialized retrievers
try:
    kb_retriever = KnowledgeBaseRetriever()
except Exception:
    print("Warning: KnowledgeBaseRetriever could not be initialized.")
    kb_retriever = None

try:
    codebase_retriever = CodebaseRetriever()
except Exception:
    print("Warning: CodebaseRetriever could not be initialized.")
    codebase_retriever = None

parser = CodeParser()

# Initialize Agents
security_agent = SecurityAgent(llm, kb_retriever)
performance_agent = PerformanceAgent(llm, kb_retriever)
quality_agent = CodeQualityAgent(llm, kb_retriever)

def parse_code_node(state: GraphState) -> Dict[str, Any]:
    """Parses the code to ensure it's valid and extract AST."""
    print("--- Parsing Code ---")
    file = state.code_file
    if not file:
        return {}
        
    try:
        ast = parser.parse(file.content, file.language)
        # Return update
        return {"parsed_ast": str(ast)}
    except Exception as e:
        print(f"Error parsing code: {e}")
        return {}

def retrieve_context_node(state: GraphState) -> Dict[str, Any]:
    """Retrieves external knowledge and codebase context."""
    print("--- Retrieving Context ---")
    file = state.code_file
    if not file: 
        return {}
    
    new_context = []
    # 1. Retrieve similar code snippets
    if codebase_retriever:
        similar_docs = codebase_retriever.retrieve_similar(file.content[:500], k=2)
        for doc in similar_docs:
            new_context.append(f"Similar Code ({doc.metadata.get('file_path')}): {doc.page_content[:200]}...")
            
    return {"retrieved_context": new_context}

def security_review_node(state: GraphState) -> Dict[str, Any]:
    print("--- Security Review ---")
    if not state.code_file: return {}
    
    review = security_agent.review(state.code_file.content, state.code_file.file_path)
    # Return update for specific key in the dict via partial dict
    return {"agent_reviews": {"security": review}}

def performance_review_node(state: GraphState) -> Dict[str, Any]:
    print("--- Performance Review ---")
    if not state.code_file: return {}
    
    review = performance_agent.review(state.code_file.content, state.code_file.file_path)
    return {"agent_reviews": {"performance": review}}

def quality_review_node(state: GraphState) -> Dict[str, Any]:
    print("--- Quality Review ---")
    if not state.code_file: return {}
    
    review = quality_agent.review(state.code_file.content, state.code_file.file_path)
    return {"agent_reviews": {"quality": review}}

def detect_conflicts_node(state: GraphState) -> Dict[str, Any]:
    """
    Identifies if agents disagree on something.
    Simple Heuristic: If one agent says X is critical, and another suggests doing X (implicit conflict),
    or mostly if they flag the SAME line.
    """
    print("--- Detecting Conflicts ---")
    # For MVP, we will assume true conflict detection is hard content-wise.
    # We will look for line overlaps where instructions differ significantly.
    # OR, we skip complex logic and just pass to resolution node.
    return {}

def resolve_conflicts_node(state: GraphState) -> Dict[str, Any]:
    """
    Uses the OrchestratorAgent to resolve conflicts and merge reviews.
    """
    print("--- Resolving and Merging ---")
    print(f"DEBUG: Agent Reviews keys: {state.agent_reviews.keys()}")
    
    if not state.code_file: return {}
    
    final_review = orchestrator_agent.resolve_conflicts_and_finalize(
        agent_reviews=state.agent_reviews,
        code_context=state.code_file.content,
        file_path=state.code_file.file_path
    )
    
    return {"final_review": final_review}

def generate_report_node(state: GraphState) -> Dict[str, Any]:
    """
    Final formatting or logging node.
    """
    print("--- Report Generated ---")
    if state.final_review:
        print(f"Summary: {state.final_review.summary}")
        print(f"Score: {state.final_review.overall_score}/10")
    return {}
