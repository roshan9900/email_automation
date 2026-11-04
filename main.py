import sys
import json
import argparse
from pathlib import Path

# Add current folder to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Ensure utf-8 encoding for standard output if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from models.schemas import EmailInput
from workflows.orchestrator import BankingEmailOrchestrator
from utils.logger import logger

BANNER = r"""
========================================================================
   HDFC Bank - Intelligent Email Processing & Customer Response System
                 Powered by Agentic AI & MCP Architecture
========================================================================
"""

def run_scenario(orchestrator: BankingEmailOrchestrator, scenario_data: dict):
    print("\n" + "=" * 80)
    print(f">> RUNNING: {scenario_data.get('name', 'Custom Query')}")
    print("=" * 80)
    print(f"[*] SENDER      : {scenario_data['sender']}")
    print(f"[*] SUBJECT     : {scenario_data['subject']}")
    print(f"[*] BODY        : \"{scenario_data['body']}\"")
    if scenario_data.get("attachment_paths"):
        print(f"[*] ATTACHMENTS : {scenario_data['attachment_paths']}")
    print("-" * 80)

    email_input = EmailInput(
        email_id=scenario_data.get("scenario_id", "DEMO-1"),
        sender=scenario_data["sender"],
        subject=scenario_data["subject"],
        body=scenario_data["body"],
        attachment_paths=scenario_data.get("attachment_paths", [])
    )

    state = orchestrator.process_email(email_input)

    print("\n[+] AGENT EXECUTION TRACE:")
    print(f"  - Session ID         : {state.session_id}")
    print(f"  - Detected Intents   : {[i.value for i in state.intent_result.intents]}")
    print(f"  - Primary Intent     : {state.intent_result.primary_intent.value}")
    print(f"  - Sentiment / Urgent : {state.sentiment_result.sentiment.value} (Urgent: {state.sentiment_result.is_urgent})")
    print(f"  - Extracted Entities : Account={state.extracted_entities.account_number}, Card={state.extracted_entities.card_number}, TxnCount={state.extracted_entities.transaction_count}, Period={state.extracted_entities.statement_period}")
    
    # Validation
    acc_v = state.validation_results.get("account_validation")
    card_v = state.validation_results.get("card_validation")
    print(f"  - Validation Status  : Account={acc_v.status.value if acc_v else 'N/A'}, Card={card_v.status.value if card_v else 'N/A'}")
    print(f"  - Partial Failure    : {state.final_response.has_partial_failure}")
    print(f"  - Total Workflow SLA : {state.total_latency_ms} ms")

    print("\n[+] GENERATED CUSTOMER RESPONSE EMAIL:")
    print("~" * 80)
    print(state.final_response.full_email_body)
    print("~" * 80)
    print(f"[!] Security Disclaimer: {state.final_response.disclaimer}\n")

def run_all_scenarios():
    print(BANNER)
    orchestrator = BankingEmailOrchestrator()
    samples_file = CURRENT_DIR / "tests" / "sample_emails.json"
    
    if not samples_file.exists():
        print(f"Error: {samples_file} not found.")
        return

    with open(samples_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    for scenario in scenarios:
        run_scenario(orchestrator, scenario)

    print("\n" + "=" * 80)
    print("[SUCCESS] All Business Scenarios & Demonstrations successfully executed!")
    print("========================================================================\n")

def interactive_mode():
    print(BANNER)
    orchestrator = BankingEmailOrchestrator()
    print("Entering interactive mode. Type 'exit' or 'quit' to terminate.\n")
    
    while True:
        try:
            body = input("\nEnter Customer Email Text > ").strip()
            if body.lower() in ["exit", "quit"]:
                break
            if not body:
                continue

            scenario = {
                "name": "Live Interactive Test",
                "sender": "customer.live@example.com",
                "subject": "Customer Inquiry",
                "body": body
            }
            run_scenario(orchestrator, scenario)
        except (KeyboardInterrupt, EOFError):
            break

def start_api_server():
    try:
        from fastapi import FastAPI
        import uvicorn
        from apis.mcp_tools import MCP_CORE_BANKING_TOOLS, execute_mcp_tool
        
        app = FastAPI(title="HDFC Bank Email Automation & MCP Server", version="1.0.0")
        orchestrator = BankingEmailOrchestrator()

        @app.get("/health")
        def health():
            return {"status": "UP", "service": "HDFC-Email-Automation-MCP"}

        @app.get("/mcp/tools")
        def list_mcp_tools():
            return {"tools": MCP_CORE_BANKING_TOOLS}

        @app.post("/mcp/execute")
        def call_tool(payload: dict):
            return execute_mcp_tool(payload.get("tool_name", ""), payload.get("arguments", {}))

        @app.post("/email/process")
        def process_incoming_email(email: EmailInput):
            state = orchestrator.process_email(email)
            return state.model_dump()

        print("\nStarting HDFC Bank MCP & Email Processing Server on port 8000...")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except ImportError:
        print("FastAPI / Uvicorn not installed. Install via `pip install fastapi uvicorn` to run server mode.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HDFC Bank Intelligent Email Processing System")
    parser.add_argument("--demo", action="store_true", default=True, help="Run all 5 standard case study scenarios")
    parser.add_argument("--interactive", action="store_true", help="Interactive testing CLI")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI & MCP API server")

    args = parser.parse_args()

    if args.serve:
        start_api_server()
    elif args.interactive:
        interactive_mode()
    else:
        run_all_scenarios()

