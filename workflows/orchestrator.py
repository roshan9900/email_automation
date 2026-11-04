import time
import uuid
from typing import Optional
from models.schemas import EmailInput, FinalEmailResponse
from workflows.state import WorkflowState
from agents.email_understanding_agent import EmailUnderstandingAgent
from agents.intent_sentiment_agent import IntentSentimentAgent
from agents.entity_extraction_agent import EntityExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.api_selection_agent import APISelectionAgent
from agents.response_generation_agent import ResponseGenerationAgent
from agents.audit_agent import AuditLoggingAgent

class BankingEmailOrchestrator:
    """
    Main Agentic Workflow Orchestrator coordinating all 7 agents in sequence,
    managing state transitions, ensuring data privacy and audit compliance.
    """
    def __init__(self):
        self.email_agent = EmailUnderstandingAgent()
        self.intent_sentiment_agent = IntentSentimentAgent()
        self.entity_agent = EntityExtractionAgent()
        self.validation_agent = ValidationAgent()
        self.api_decision_agent = APISelectionAgent()
        self.response_agent = ResponseGenerationAgent()
        self.audit_agent = AuditLoggingAgent()

    def process_email(self, email_input: EmailInput) -> WorkflowState:
        session_id = f"SESSION-{uuid.uuid4().hex[:8].upper()}"
        start_overall = time.time()
        
        state = WorkflowState(
            session_id=session_id,
            email_input=email_input,
            status="RUNNING"
        )

        try:
            # Step 1: Email Understanding & Preprocessing
            understanding_res = self.email_agent.process(email_input)
            state.email_cleaned_text = understanding_res["clean_body"]
            state.attachment_content = understanding_res["attachment_text"]
            combined_text = understanding_res["combined_content"]

            # Step 2: Intent Detection & Sentiment Analysis
            intent_res, sentiment_res = self.intent_sentiment_agent.process(combined_text)
            state.intent_result = intent_res
            state.sentiment_result = sentiment_res

            # Step 3: Entity Extraction
            entities = self.entity_agent.process(combined_text)
            state.extracted_entities = entities

            # Step 4: Validation against Core Banking Systems
            validation_res = self.validation_agent.process(entities)
            state.validation_results = validation_res

            # Step 5: API Decision Engine (Plan & Execute via MCP tools)
            exec_res = self.api_decision_agent.plan_and_execute(
                intent_result=intent_res,
                entities=entities,
                validation_results=validation_res
            )
            state.api_execution_plan = exec_res["execution_plan"]
            state.api_results = exec_res["api_results"]

            # Step 6: Response Generation
            cust_name = ""
            if validation_res.get("account_validation") and validation_res["account_validation"].customer_name:
                cust_name = validation_res["account_validation"].customer_name
            elif validation_res.get("card_validation") and validation_res["card_validation"].card_holder:
                cust_name = validation_res["card_validation"].card_holder

            final_email: FinalEmailResponse = self.response_agent.generate(
                recipient_email=email_input.sender,
                customer_name=cust_name,
                sentiment_res=sentiment_res,
                entities=entities,
                validation_results=validation_res,
                api_results=exec_res["api_results"]
            )
            state.final_response = final_email
            state.status = "SUCCESS"

        except Exception as e:
            state.status = "ERROR"
            state.errors.append(str(e))
            # Fallback error response
            state.final_response = FinalEmailResponse(
                recipient_email=email_input.sender,
                subject="HDFC Bank - Service Notification",
                greeting="Dear Customer,",
                full_email_body="We experienced an unexpected issue processing your request. Our support team has been notified.",
                has_partial_failure=True
            )

        total_latency = (time.time() - start_overall) * 1000
        state.total_latency_ms = round(total_latency, 2)

        # Audit record
        self.audit_agent.record_run(
            session_id=session_id,
            email_id=email_input.email_id or "UNKNOWN",
            status=state.status,
            summary={
                "intents": [i.value for i in state.intent_result.intents] if state.intent_result else [],
                "sentiment": state.sentiment_result.sentiment.value if state.sentiment_result else "UNKNOWN",
                "total_latency_ms": state.total_latency_ms,
                "has_partial_failure": state.final_response.has_partial_failure if state.final_response else False
            }
        )

        return state

