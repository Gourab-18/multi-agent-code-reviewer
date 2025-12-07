import sys
import os
import unittest
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.graph.workflow import ReviewOrchestrator
from src.models.schemas import FinalReview

load_dotenv()

# Complex intentionally bad code
BAD_CODE_SCENARIO = """
import sqlite3
import os

def process_orders(user_input):
    # SECURITY: Hardcoded secret
    api_token = "sk-ADMIN12345SECRET" 
    
    # SECURITY: SQL Injection
    query = "SELECT * FROM orders WHERE user_id = " + user_input 
    
    orders = []
    
    # PERFORMANCE: Doing DB connection inside loop (if this loop was real)
    # QUALITY: Magic number '500'
    limit = 500
    
    # COMPLEXITY: Deep nesting example
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("Too deep")

    return query
"""

class TestReviewWorkflow(unittest.TestCase):
    def setUp(self):
        self.orchestrator = ReviewOrchestrator()
        
    def test_review_code_e2e(self):
        print("\n\n=== Starting E2E Workflow Test ===")
        try:
            review = self.orchestrator.review_code(
                code=BAD_CODE_SCENARIO,
                language="python",
                file_path="src/legacy/order_processor.py"
            )
            
            print(f"\nReview Generated for {review.file_path}")
            print(f"Overall Score: {review.overall_score}/10")
            print(f"Summary: {review.summary}")
            
            print("\nFindings:")
            found_secrets = False
            found_sqli = False
            found_nesting = False
            
            for f in review.all_findings:
                # Debug print
                print(f" - [{f.severity}] {f.category or 'Unknown'}: {f.description}")
                
                desc_lower = f.description.lower()
                # Check coverage of expected issues
                if "secret" in desc_lower or "api_token" in desc_lower or "credential" in desc_lower:
                    found_secrets = True
                if "sql" in desc_lower or "injection" in desc_lower:
                    found_sqli = True
                if "nesting" in desc_lower or "deep" in desc_lower or "complexity" in desc_lower:
                    found_nesting = True
            
            # Assertions
            self.assertTrue(found_secrets, "Should detect hardcoded secret")
            self.assertTrue(found_sqli, "Should detect SQL injection")
            # Quality checks might vary based on threshold, but let's check score
            self.assertLess(review.overall_score, 8.0, "Score should be low for bad code")
            
        except Exception as e:
            self.fail(f"Workflow failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
