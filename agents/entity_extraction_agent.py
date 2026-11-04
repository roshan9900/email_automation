import time
import json
from models.schemas import ExtractedEntities
from models.llm_provider import get_llm_provider
from prompts.templates import ENTITY_EXTRACTION_SYSTEM_PROMPT
from utils.logger import log_audit_event

class EntityExtractionAgent:
    """
    Agent 4: Responsible for extracting key banking entities:
    account numbers, card numbers, transaction counts, dates/periods.
    """
    def __init__(self):
        self.name = "EntityExtractionAgent"
        self.llm = get_llm_provider()

    def process(self, email_text: str) -> ExtractedEntities:
        start_time = time.time()
        
        prompt = f"Please extract entities from this banking email:\n\n{email_text}"
        response_str = self.llm.complete(prompt=prompt, system_prompt=ENTITY_EXTRACTION_SYSTEM_PROMPT)

        try:
            data = json.loads(response_str)
        except Exception:
            data = {}

        entities = ExtractedEntities(
            account_number=data.get("account_number"),
            card_number=data.get("card_number"),
            transaction_count=data.get("transaction_count") or 5,
            statement_period=data.get("statement_period"),
            customer_name=data.get("customer_name")
        )

        elapsed = (time.time() - start_time) * 1000
        log_audit_event(
            agent_name=self.name,
            step="EntityExtraction",
            details={
                "account_number_found": bool(entities.account_number),
                "card_number_found": bool(entities.card_number),
                "statement_period": entities.statement_period,
                "transaction_count": entities.transaction_count
            },
            execution_time_ms=elapsed
        )
        return entities

