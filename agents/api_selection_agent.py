import time
from typing import List, Dict, Any
from models.schemas import (
    IntentType,
    ValidationStatus,
    ExtractedEntities,
    IntentDetectionResult
)
from apis.mcp_tools import execute_mcp_tool
from utils.logger import log_audit_event

class APISelectionAgent:
    """
    Agent 6: API Decision Engine.
    Determines which Core Banking APIs to invoke, identifies parallel execution paths,
    executes them through the MCP tools interface, and collects outputs.
    """
    def __init__(self):
        self.name = "APISelectionAgent"

    def plan_and_execute(
        self,
        intent_result: IntentDetectionResult,
        entities: ExtractedEntities,
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        execution_plan: List[Dict[str, Any]] = []
        api_results: Dict[str, Any] = {}

        # 1. Evaluate Balance Request
        if IntentType.ACCOUNT_BALANCE in intent_result.intents:
            acc_val = validation_results.get("account_validation")
            if acc_val and acc_val.status == ValidationStatus.VALID:
                execution_plan.append({
                    "tool": "GetAccountBalanceAPI",
                    "args": {"account_number": entities.account_number},
                    "intent": "ACCOUNT_BALANCE"
                })
            else:
                api_results["ACCOUNT_BALANCE"] = {
                    "status": "VALIDATION_FAILED",
                    "error": acc_val.error_message if acc_val else "Account number missing or invalid."
                }

        # 2. Evaluate Credit Card Transactions Request
        if IntentType.CREDIT_CARD_USAGE in intent_result.intents:
            card_val = validation_results.get("card_validation")
            if card_val and card_val.status == ValidationStatus.VALID:
                execution_plan.append({
                    "tool": "GetCardTransactionsAPI",
                    "args": {
                        "card_number": entities.card_number,
                        "limit": entities.transaction_count or 5
                    },
                    "intent": "CREDIT_CARD_USAGE"
                })
            else:
                api_results["CREDIT_CARD_USAGE"] = {
                    "status": "VALIDATION_FAILED",
                    "error": card_val.error_message if card_val else "Credit card number missing or invalid."
                }

        # 3. Evaluate Statement Request
        if IntentType.STATEMENT_REQUEST in intent_result.intents:
            acc_val = validation_results.get("account_validation")
            period = entities.statement_period or "April 2026"
            if acc_val and acc_val.status == ValidationStatus.VALID:
                execution_plan.append({
                    "tool": "GetStatementAPI",
                    "args": {
                        "account_number": entities.account_number,
                        "period": period
                    },
                    "intent": "STATEMENT_REQUEST"
                })
            else:
                api_results["STATEMENT_REQUEST"] = {
                    "status": "VALIDATION_FAILED",
                    "error": acc_val.error_message if acc_val else "Account number required for statement generation."
                }

        # Parallel / Sequential Execution of scheduled calls via MCP Tool dispatcher
        for plan_item in execution_plan:
            tool_name = plan_item["tool"]
            args = plan_item["args"]
            intent_key = plan_item["intent"]
            
            call_start = time.time()
            output = execute_mcp_tool(tool_name, args)
            call_latency = (time.time() - call_start) * 1000
            
            api_results[intent_key] = output
            log_audit_event(
                agent_name=self.name,
                step=f"ToolExecution_{tool_name}",
                details={"arguments": args, "status": output.get("status")},
                execution_time_ms=call_latency
            )

        elapsed = (time.time() - start_time) * 1000
        log_audit_event(
            agent_name=self.name,
            step="APIDecisionEngineCompleted",
            details={"planned_calls": len(execution_plan), "executed": list(api_results.keys())},
            execution_time_ms=elapsed
        )
        return {
            "execution_plan": execution_plan,
            "api_results": api_results
        }

