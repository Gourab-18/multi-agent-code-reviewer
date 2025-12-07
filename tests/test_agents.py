import sys
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.models.schemas import CodeFile, GraphState, ReviewFinding, Severity, AgentReview, Category
from src.agents.security_agent import SecurityAgent
from src.agents.performance_agent import PerformanceAgent
from src.agents.quality_agent import CodeQualityAgent
from src.graph.nodes import resolve_conflicts_node

load_dotenv()

# Sample code with intentional flaws
BAD_CODE = """
import os
import requests

def get_user_data(user_ids):
    api_key = "sk-1234567890abcdef12345678" # Hardcoded secret
    
    results = []
    for uid in user_ids:
        # N+1 problem and potential SQL injection if this was a DB query
        # Also minimal error handling
        response = requests.get(f"https://api.example.com/users/{uid}?token={api_key}")
        data = response.json()
        results.append(data)
        
    return results

def complex_logic(x):
    # Cyclomatic complexity, deep nesting, bad naming
    if x > 0:
        if x < 100:
            if x % 2 == 0:
                for i in range(x):
                    if i > 50:
                        print("high")
                    else:
                        print("low")
    return True
"""

def test_agents():
    print("=== Testing Agents ===")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # 1. Test Security Agent
    print("\n--- Security Agent ---")
    sec_agent = SecurityAgent(llm=llm) # skipping retriever for simple unit test or mock it if needed
    sec_review = sec_agent.review(BAD_CODE, "bad_code.py")
    print(f"Confidence: {sec_review.confidence_score}")
    for f in sec_review.findings:
        print(f"[{f.severity}] {f.description}")
        
    # 2. Test Performance Agent
    print("\n--- Performance Agent ---")
    perf_agent = PerformanceAgent(llm=llm)
    perf_review = perf_agent.review(BAD_CODE, "bad_code.py")
    print(f"Confidence: {perf_review.confidence_score}")
    for f in perf_review.findings:
        print(f"[{f.severity}] {f.description}")

    # 3. Test Quality Agent
    print("\n--- Quality Agent ---")
    qual_agent = CodeQualityAgent(llm=llm)
    qual_review = qual_agent.review(BAD_CODE, "bad_code.py")
    print(f"Confidence: {qual_review.confidence_score}")
    for f in qual_review.findings:
        print(f"[{f.severity}] {f.description}")

    return {
        "security": sec_review,
        "performance": perf_review,
        "quality": qual_review
    }

def test_conflict_resolution(reviews):
    print("\n=== Testing Conflict Resolution Node ===")
    
    # Construct state
    code_file = CodeFile(file_path="bad_code.py", content=BAD_CODE, language="python")
    state = GraphState(
        code_file=code_file,
        agent_reviews=reviews,
        conflicts=[],
        retrieved_context=[]
    )
    
    # Run node
    new_state = resolve_conflicts_node(state)
    
    if new_state.final_review:
        print("\nFinal Consolidated Review:")
        print(f"Summary: {new_state.final_review.summary}")
        print(f"Overall Score: {new_state.final_review.overall_score}")
        print("\nFindings:")
        for f in new_state.final_review.all_findings:
            print(f"- {f.description}")
    else:
        print("Error: No Final Review generated.")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set.")
        sys.exit(1)
        
    reviews = test_agents()
    test_conflict_resolution(reviews)
