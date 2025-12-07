from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Enums for standardized values
class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class Category(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    STYLE = "style"  # Added style as a common category
    MAINTAINABILITY = "maintainability"

class CodeFile(BaseModel):
    """Represents a source code file to be reviewed."""
    file_path: str = Field(..., description="The relative path to the file", examples=["src/main.py"])
    content: str = Field(..., description="The full content of the file")
    language: str = Field(..., description="The programming language of the file", examples=["python", "javascript"])

class ReviewFinding(BaseModel):
    """Represents a single issue or finding discovered during review."""
    severity: Severity = Field(..., description="The severity level of the finding")
    category: Category = Field(..., description="The category of the issue")
    line_number: Optional[int] = Field(None, description="The line number where the issue occurs (1-based)")
    description: str = Field(..., description="Detailed description of the issue")
    suggestion: str = Field(..., description="Actionable suggestion to fix or improve the code")
    agent_source: str = Field(..., description="The name of the agent that found this issue", examples=["SecurityAgent", "LintingAgent"])

class AgentReview(BaseModel):
    """Output from a single agent's review."""
    agent_name: str = Field(..., description="Name of the agent performing the review")
    findings: List[ReviewFinding] = Field(default_factory=list, description="List of findings identified by the agent")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the review (0.0 to 1.0)")

class ConflictResolution(BaseModel):
    """Represents the resolution of a disagreement between agents."""
    conflicting_findings: List[ReviewFinding] = Field(..., description="The findings that were in conflict")
    resolution: str = Field(..., description="The final decision or resolution")
    reasoning: str = Field(..., description="Explanation of why this resolution was chosen")

class FinalReview(BaseModel):
    """The consolidated final review output."""
    file_path: str = Field(..., description="Path of the reviewed file")
    all_findings: List[ReviewFinding] = Field(..., description="Consolidated list of accepted findings")
    conflicts_resolved: List[ConflictResolution] = Field(default_factory=list, description="Resolutions for any conflicts encountered")
    summary: str = Field(..., description="Executive summary of the code review")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall quality score (0-10)")

class GraphState(BaseModel):
    """The state object for the LangGraph state machine."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    code_file: Optional[CodeFile] = Field(None, description="The file currently being processed")
    parsed_ast: Optional[Any] = Field(None, description="The parsed Abstract Syntax Tree (AST)")
    retrieved_context: List[str] = Field(default_factory=list, description="Relevant context retrieved from knowledge base")
    agent_reviews: Dict[str, AgentReview] = Field(default_factory=dict, description="Reviews collected from different agents, keyed by agent name")
    conflicts: List[ConflictResolution] = Field(default_factory=list, description="Resolved conflicts during the process")
    final_review: Optional[FinalReview] = Field(None, description="The final generated review output")
