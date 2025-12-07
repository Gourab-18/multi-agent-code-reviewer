from typing import Any, Dict, List
import os

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from src.models.schemas import GraphState, CodeFile, FinalReview
from src.graph.nodes import (
    parse_code_node,
    retrieve_context_node,
    security_review_node,
    performance_review_node,
    quality_review_node,
    detect_conflicts_node,
    resolve_conflicts_node,
    generate_report_node
)

class ReviewOrchestrator:
    """
    Orchestrates the multi-agent code review process using LangGraph.
    """
    
    def __init__(self):
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
    def _build_workflow(self) -> StateGraph:
        """Constructs the state graph."""
        workflow = StateGraph(GraphState)
        
        # 1. Add Nodes
        workflow.add_node("parse_code", parse_code_node)
        workflow.add_node("retrieve_context", retrieve_context_node)
        
        workflow.add_node("security_review", security_review_node)
        workflow.add_node("performance_review", performance_review_node)
        workflow.add_node("quality_review", quality_review_node)
        
        workflow.add_node("detect_conflicts", detect_conflicts_node)
        workflow.add_node("resolve_conflicts", resolve_conflicts_node)
        workflow.add_node("generate_report", generate_report_node)
        
        # 2. Add Edges
        # START -> Parse
        workflow.set_entry_point("parse_code")
        
        # Parse -> Retrieve
        workflow.add_edge("parse_code", "retrieve_context")
        
        # Retrieve -> Fan Out (Parallel)
        workflow.add_edge("retrieve_context", "security_review")
        workflow.add_edge("retrieve_context", "performance_review")
        workflow.add_edge("retrieve_context", "quality_review")
        
        # Fan In -> Detect Conflicts
        workflow.add_edge("security_review", "detect_conflicts")
        workflow.add_edge("performance_review", "detect_conflicts")
        workflow.add_edge("quality_review", "detect_conflicts")
        
        # Detect -> Resolve (Unconditional for now as detect logic is simple)
        # In a real system, we'd use a conditional edge based on state.conflicts
        workflow.add_edge("detect_conflicts", "resolve_conflicts")
        
        # Resolve -> Report
        workflow.add_edge("resolve_conflicts", "generate_report")
        
        # Report -> END
        workflow.add_edge("generate_report", END)
        
        return workflow

    def save_graph_image(self, output_path: str = "graph_diagram.png"):
        """Saves a visualization of the graph."""
        try:
            db_graph = self.app.get_graph()
            db_graph.draw_mermaid_png(output_path) # Needs IoC usually or specific setup
            # Alternatively use print_ascii
            print("Graph structure:")
            db_graph.print_ascii()
        except Exception as e:
            print(f"Could not draw graph: {e}")

    def review_code(self, code: str, language: str = "python", file_path: str = "snippet") -> FinalReview:
        """
        Runs the full review workflow on a code string.
        """
        # Initialize state
        initial_state = GraphState(
            code_file=CodeFile(
                file_path=file_path,
                content=code,
                language=language
            ),
            conflicts=[],
            retrieved_context=[]
        )
        
        # Run graph
        # invoke returns the final state
        final_state = self.app.invoke(initial_state)
        
        if final_state.get("final_review"):
            return final_state["final_review"]
        else:
            raise ValueError("Review failed to generate a final report.")

    def review_file(self, file_path: str) -> FinalReview:
        """
        Runs the full review workflow on a file from disk.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        language = "python"
        if file_path.endswith((".js", ".jsx")): language = "javascript"
        elif file_path.endswith((".ts", ".tsx")): language = "typescript"
        
        return self.review_code(content, language, file_path)
