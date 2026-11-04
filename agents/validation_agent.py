import time
from typing import Dict, Any, Optional
from models.schemas import (
    ExtractedEntities,
    ValidationStatus,
    AccountValidationResult,
    CardValidationResult
)
from apis.mock_core_banking import banking_service
from utils.logger import log_audit_event

class ValidationAgent:
    """
    Agent 5: Validates extracted entities against Core Banking APIs.
    Identifies invalid accounts, blocked cards, or nonexistent records.
    """
    def __init__(self):
        self.name = "ValidationAgent"

    def process(self, entities: ExtractedEntities) -> Dict[str, Any]:
        start_time = time.time()
        results: Dict[str, Any] = {
            "account_validation": None,
            "card_validation": None,
            "is_all_valid": True,
            "has_partial_failure": False
        }

        # Validate Account if present
        if entities.account_number:
            acc_val: AccountValidationResult = banking_service.validate_account(entities.account_number)
            results["account_validation"] = acc_val
            if acc_val.status != ValidationStatus.VALID:
                results["is_all_valid"] = False

        # Validate Card if present
        if entities.card_number:
            card_val: CardValidationResult = banking_service.validate_card(entities.card_number)
            results["card_validation"] = card_val
            if card_val.status != ValidationStatus.VALID:
                results["is_all_valid"] = False

        # Check for partial validation scenario (e.g., account valid, card invalid)
        has_acc = results["account_validation"] is not None
        has_card = results["card_validation"] is not None

        if has_acc and has_card:
            acc_ok = results["account_validation"].status == ValidationStatus.VALID
            card_ok = results["card_validation"].status == ValidationStatus.VALID
            if (acc_ok and not card_ok) or (card_ok and not acc_ok):
                results["has_partial_failure"] = True

        elapsed = (time.time() - start_time) * 1000
        log_audit_event(
            agent_name=self.name,
            step="EntityValidation",
            details={
                "account_valid": results["account_validation"].status.value if results["account_validation"] else "N/A",
                "card_valid": results["card_validation"].status.value if results["card_validation"] else "N/A",
                "has_partial_failure": results["has_partial_failure"]
            },
            execution_time_ms=elapsed
        )
        return results

