from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

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
    # We allow uppercase strings to pass Groq's strict schema validation
    # then normalize them using the validator below.
    severity: str = Field(description="critical, warning, or info")
    category: Category = Field(description="Category of the issue")
    line_number: Optional[int] = Field(None, description="Line number where issue occurs")
    description: str = Field(description="Description of the finding")
    suggestion: str = Field(description="Actionable fix suggestion")
    agent_source: Optional[str] = Field(None, description="Name of agent that found this")

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v):
        if isinstance(v, str):
            v = v.lower()
        # Validate that it is a valid severity after normalization
        if v not in ["critical", "warning", "info"]:
             # Fallback or error? Let's fallback to info
             return "info"
        return v

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

from operator import add
from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

# Helper for merging dictionaries in LangGraph state updates
def merge_dicts(a: Dict, b: Dict) -> Dict:
    return {**a, **b}

# ... (Previous Enums/Classes CodeFile, ReviewFinding, AgentReview, ConflictResolution, FinalReview omitted to save tokens, assuming they are preserved)

class GraphState(BaseModel):
    """The state object for the LangGraph state machine."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    code_file: Optional[CodeFile] = Field(None, description="The file currently being processed")
    parsed_ast: Optional[Any] = Field(None, description="The parsed Abstract Syntax Tree (AST)")
    
    # Use Annotated with 'add' operator to append to list for retrieved_context (if multiple nodes added to it, though here mostly sequential)
    # But strictly for agent_reviews which IS parallel, we need a merger.
    retrieved_context: Annotated[List[str], add] = Field(default_factory=list, description="Relevant context retrieved from knowledge base")
    
    # Use merge_dicts for agent reviews to allow parallel agents to update different keys
    agent_reviews: Annotated[Dict[str, AgentReview], merge_dicts] = Field(default_factory=dict, description="Reviews collected from different agents")
    
    conflicts: List[ConflictResolution] = Field(default_factory=list, description="Resolved conflicts during the process")
    final_review: Optional[FinalReview] = Field(None, description="The final generated review output")
