from abc import ABC, abstractmethod
from typing import List, Optional, Any
import json

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool

from src.models.schemas import AgentReview, ReviewFinding, Severity
from src.rag.knowledge_base import KnowledgeBaseRetriever

class BaseReviewAgent(ABC):
    """
    Abstract base class for all specialized code review agents.
    Handles RAG retrieval, prompt construction, and LLM interaction.
    """
    
    def __init__(
        self, 
        name: str,
        llm: ChatOpenAI, 
        retriever: Optional[KnowledgeBaseRetriever] = None,
        tools: Optional[List[BaseTool]] = None
    ):
        self.name = name
        self.llm = llm
        self.retriever = retriever
        self.tools = tools or []
        
        # Bind tools to LLM if available
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm

        # Structure output to ensure it matches Schema
        # We use .with_structured_output to force the Pydantic model response
        self.structured_llm = self.llm.with_structured_output(AgentReview)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Returns the specialized system prompt for the agent."""
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """Returns the category this agent specializes from (security, performance, quality)."""
        pass

    def review(self, code: str, file_path: str) -> AgentReview:
        """
        Main method to perform a review on a piece of code.
        """
        # 1. Retrieve Knowledge Base context if available
        context_str = ""
        retrieved_docs = []
        if self.retriever:
            # We assume the retriever takes a query. 
            # Ideally we would generate a query, but using the file content summary or category is a good start.
            # For simplicity, we query based on the agent category + generic terms
            # In a more advanced version, we'd summarize the code first to generate a query.
            retrieved_docs = self.retriever.retrieve(
                query=f"{self.get_category()} best practices for {file_path}", 
                category=self.get_category(),
                k=3
            )
            
            if retrieved_docs:
                context_str = "\n".join([f"- {doc.page_content[:300]}..." for doc in retrieved_docs])
                context_str = f"\nRelevant Knowledge Base Guidelines:\n{context_str}\n"

        # 2. Tool Execution (Optional: Pre-analysis)
        # In a ReAct loop we would let the LLM call tools. 
        # Here, for the 'review' method, we might want to just let the LLM see the code and decide.
        # But if we want it to use tools, we need a loop.
        # For this BaseAgent using structured output directly, we imply a single-shot analysis 
        # enriched by tool outputs if we manually run them, or we rely on the LLM's internal knowledge.
        
        # NOTE: Structured Output usually doesn't mix well with Tool Calling loop in a single step 
        # unless using an agent executor.
        # To keep it simple but powerful:
        # We will RUN the analyzers relevant to this agent FIRST if they exist in self.tools,
        # and feed their output as context.
        
        tool_outputs = ""
        if self.tools:
            tool_outputs = "\nAutomated Tool Analysis:\n"
            for tool in self.tools:
                try:
                    # We pass the code to the tool. Most of our tools in analyzers.py take 'code'.
                    # Some take 'language'. We infer language from file_path.
                    language = "python"
                    if file_path.endswith((".js", ".ts", ".jsx", ".tsx")):
                        language = "javascript"

                    # Check tool schema to see what args it needs
                    # This is a bit hacky for a generic base, but works for our specific tools
                    tool_args = {}
                    if "code" in tool.args:
                        tool_args["code"] = code
                    if "language" in tool.args:
                        tool_args["language"] = language
                        
                    res = tool.invoke(tool_args)
                    if res:
                         tool_outputs += f"- {tool.name}: {res}\n"
                except Exception as e:
                    print(f"Error running tool {tool.name}: {e}")

        # 3. Construct Prompt
        system_prompt = self.get_system_prompt()
        
        full_prompt = f"""
{system_prompt}

You are reviewing the file: {file_path}

{context_str}

{tool_outputs}

Instructions:
1. Analyze the provided code.
2. Consider the automated tool findings and the knowledge base guidelines.
3. Identify specific issues related to your specialty ({self.get_category()}).
4. Provide actionable suggestions.
5. Rate your confidence.
6. Return the output STRICTLY matching the 'AgentReview' schema.
"""
        
        messages = [
            SystemMessage(content=full_prompt),
            HumanMessage(content=f"Code to review:\n\n{code}")
        ]

        # 4. Invoke LLM with Structured Output
        # Note: We are putting the 'agent_name' in the prompt/system message, 
        # but the model needs to fill it in schema. We can override it or ask model to do it.
        # It's safer to override it after.
        
        try:
            result = self.structured_llm.invoke(messages)
            
            # Enforce agent name correctness
            if isinstance(result, AgentReview):
                result.agent_name = self.name
                
            return result
        except Exception as e:
            print(f"Error in agent review: {e}")
            # Return empty review on failure
            return AgentReview(
                agent_name=self.name,
                findings=[ReviewFinding(
                    severity=Severity.INFO, 
                    category=self.get_category(), # type: ignore
                    description=f"Review failed: {str(e)}", 
                    suggestion="Check logs", 
                    agent_source=self.name
                )],
                confidence_score=0.0
            )
