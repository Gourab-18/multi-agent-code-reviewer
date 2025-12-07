import argparse
import sys
import os
from dotenv import load_dotenv

# Add src to path just in case
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.graph.workflow import ReviewOrchestrator

def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please check your .env file.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Multi-Agent Code Reviewer")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Review File Command
    review_parser = subparsers.add_parser("review", help="Review a source code file")
    review_parser.add_argument("file", help="Path to the file to review")
    review_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    # Review String Command (mostly for testing)
    scan_parser = subparsers.add_parser("scan", help="Review a code snippet from stdin/arg")
    scan_parser.add_argument("--code", help="Code string", required=False)
    
    args = parser.parse_args()

    if args.command in ["review", "scan"]:
        print("Initializing Agents and Workflow...")
        try:
            orchestrator = ReviewOrchestrator()
            
            result = None
            if args.command == "review":
                print(f"Reviewing file: {args.file}...")
                result = orchestrator.review_file(args.file)
            elif args.command == "scan":
                code = args.code
                if not code:
                    print("Reading from stdin...")
                    code = sys.stdin.read()
                print("Reviewing code snippet...")
                result = orchestrator.review_code(code, file_path="stdin")

            if result:
                print("\n" + "="*50)
                print(f" FINAL REVIEW REPORT ({result.overall_score}/10)")
                print("="*50)
                print(f"\nSUMMARY:\n{result.summary}\n")
                
                print("FINDINGS:")
                # Sort by severity
                severity_order = {"critical": 0, "warning": 1, "info": 2}
                sorted_findings = sorted(result.all_findings, key=lambda x: severity_order.get(x.severity, 3))
                
                for f in sorted_findings:
                    print(f"[{f.severity.upper()}] {f.category.upper()} (Line {f.line_number or '?'}):")
                    print(f"  Issue: {f.description}")
                    print(f"  Fix:   {f.suggestion}")
                    print("-" * 30)
                    
            else:
                print("No review generated.")
                
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
