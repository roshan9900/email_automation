import os
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

from config.settings import LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL
from models.schemas import EmailInput
from models.llm_provider import OllamaLLMProvider
from workflows.orchestrator import BankingEmailOrchestrator
from utils.logger import logger

def get_banner():
    return f"""========================================================================
   HDFC Bank - Intelligent Email Processing & Customer Response System
                 Powered by Agentic AI & Local Ollama (LLaMA 3)
========================================================================
[*] Local LLM Provider : {LLM_PROVIDER.upper()}
[*] Ollama Host URL    : {OLLAMA_BASE_URL}
[*] Target Model       : {OLLAMA_MODEL}
========================================================================"""

def check_ollama_status():
    print(get_banner())
    print("\n[+] Probing Local Ollama Service...")
    provider = OllamaLLMProvider()
    status = provider.check_connection()

    if status.get("online"):
        print(f"[OK] Ollama is ONLINE at: {status.get('base_url')}")
        installed = status.get("installed_models", [])
        print(f"[+] Installed Models ({len(installed)}): {', '.join(installed) if installed else 'None'}")
        if status.get("model_ready"):
            print(f"[OK] Target model '{status.get('target_model')}' is installed and ready for inference!")
        else:
            print(f"[!] Target model '{status.get('target_model')}' is NOT in installed models.")
            print(f"[TIP] Download it by running: ollama pull {status.get('target_model')}")
    else:
        print(f"[!] Ollama is OFFLINE or unreachable at {status.get('base_url')}.")
        print("[TIP] To start Ollama on your machine:")
        print("      1. Start Ollama service: ollama serve")
        print(f"      2. Pull the model       : ollama pull {status.get('target_model')}")
        print("      (The system will use the resilient offline banking engine in the meantime)\n")

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
    print(f"  - Status             : {state.status}")
    if state.status == "FAILED" or not state.intent_result:
        print(f"  - Failure Reason     : {'; '.join(state.errors) if state.errors else 'Unknown pipeline error'}")
        if state.final_response:
            print("\n[+] GENERATED CUSTOMER RESPONSE EMAIL:")
            print("~" * 80)
            print(state.final_response.full_email_body)
            print("~" * 80)
        print("-" * 80 + "\n")
        return

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
    print(get_banner())
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
    print(get_banner())
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
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse, RedirectResponse
        import uvicorn
        from apis.mcp_tools import MCP_CORE_BANKING_TOOLS, execute_mcp_tool
        from workflows.hitl_manager import hitl_manager
        from models.llm_provider import OllamaLLMProvider
        
        app = FastAPI(title="HDFC Bank Email Automation & MCP Server", version="1.0.0")
        orchestrator = BankingEmailOrchestrator()

        dashboard_file = CURRENT_DIR / "apis" / "dashboard.html"

        @app.get("/", include_in_schema=False)
        def root():
            return RedirectResponse(url="/dashboard")

        @app.get("/dashboard", response_class=HTMLResponse)
        def get_dashboard():
            if dashboard_file.exists():
                return dashboard_file.read_text(encoding="utf-8")
            return "<h1>HDFC Bank Dashboard not found.</h1>"

        @app.get("/health")
        def health():
            return {
                "status": "UP",
                "service": "HDFC-Email-Automation-MCP",
                "provider": LLM_PROVIDER,
                "model": OLLAMA_MODEL
            }

        @app.get("/api/ollama/status")
        def get_ollama_status():
            prov = OllamaLLMProvider()
            return prov.check_connection()

        @app.get("/mcp/tools")
        def list_mcp_tools():
            return {"tools": MCP_CORE_BANKING_TOOLS}

        @app.post("/mcp/execute")
        def call_tool(payload: dict):
            return execute_mcp_tool(payload.get("tool_name", ""), payload.get("arguments", {}))

        @app.post("/email/process")
        def process_incoming_email(email: EmailInput):
            try:
                state = orchestrator.process_email(email)
                return state.model_dump()
            except ConnectionRefusedError as ce:
                raise HTTPException(
                    status_code=503,
                    detail=f"Ollama server is offline ({ce}). Please run 'ollama serve' in your terminal or launch the Ollama app."
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/hitl/queue")
        def list_hitl_queue():
            return {"pending_reviews": hitl_manager.get_pending_reviews()}

        @app.post("/hitl/approve/{session_id}")
        def approve_hitl(session_id: str):
            res = hitl_manager.approve(session_id)
            return {"status": "SUCCESS" if res else "NOT_FOUND", "item": res}

        print("\n" + "=" * 80)
        print(">> HDFC Bank MCP & Email Processing Server Starting...")
        print(">> Live Web Dashboard : http://127.0.0.1:8000/dashboard")
        print(">> MCP Tools Endpoint : http://127.0.0.1:8000/mcp/tools")
        print(">> API Swagger Docs   : http://127.0.0.1:8000/docs")
        print("=" * 80 + "\n")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except ImportError:
        print("FastAPI / Uvicorn not installed. Install via `pip install fastapi uvicorn` to run server mode.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HDFC Bank Intelligent Email Processing System (Local Ollama)")
    parser.add_argument("--demo", action="store_true", default=False, help="Run all 5 standard case study scenarios")
    parser.add_argument("--interactive", action="store_true", help="Interactive testing CLI")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI & MCP API server")
    parser.add_argument("--check-ollama", action="store_true", help="Check local Ollama daemon connection and model status")
    parser.add_argument("--model", type=str, default="", help="Override target Ollama model name (e.g. llama3, llama3.2, mistral)")
    parser.add_argument("--ollama-url", type=str, default="", help="Override Ollama base URL (e.g. http://localhost:11434)")

    args = parser.parse_args()

    # Apply command line overrides if provided
    if args.model:
        os.environ["OLLAMA_MODEL"] = args.model
    if args.ollama_url:
        os.environ["OLLAMA_BASE_URL"] = args.ollama_url

    if args.check_ollama:
        check_ollama_status()
    elif args.serve:
        start_api_server()
    elif args.interactive:
        interactive_mode()
    else:
        run_all_scenarios()
