import time
from typing import Dict, Any
from models.schemas import (
    FinalEmailResponse,
    SentimentType,
    SentimentAnalysisResult,
    ExtractedEntities,
    ValidationStatus
)
from utils.security_masker import mask_account_number, mask_card_number, mask_currency
from utils.logger import log_audit_event
from config.settings import BANK_NAME, SUPPORT_PHONE, SUPPORT_EMAIL

class ResponseGenerationAgent:
    """
    Agent 7: Generates professional, compliant banking response emails.
    Consolidates multiple intents, applies strict PII/card masking,
    handles partial validation failures, and adjusts tone according to sentiment.
    """
    def __init__(self):
        self.name = "ResponseGenerationAgent"

    def generate(
        self,
        recipient_email: str,
        customer_name: str,
        sentiment_res: SentimentAnalysisResult,
        entities: ExtractedEntities,
        validation_results: Dict[str, Any],
        api_results: Dict[str, Any]
    ) -> FinalEmailResponse:
        start_time = time.time()
        
        greeting = f"Dear {customer_name}," if customer_name and customer_name != "John Doe" else "Dear Customer,"
        
        sections: Dict[str, str] = {}
        has_failure = False
        has_success = False

        # 1. Account Balance Section
        if "ACCOUNT_BALANCE" in api_results:
            res = api_results["ACCOUNT_BALANCE"]
            if res.get("status") == "SUCCESS":
                has_success = True
                masked_acc = mask_account_number(res.get("account_number", entities.account_number))
                formatted_bal = mask_currency(res.get("balance", 0.0))
                acc_type = res.get("account_type", "Account")
                sections["Account Balance"] = (
                    f"Account Balance ({acc_type}):\n"
                    f"• Account Number: {masked_acc}\n"
                    f"• Available Balance: {formatted_bal}"
                )
            else:
                has_failure = True
                masked_acc = mask_account_number(entities.account_number or "")
                sections["Account Balance"] = (
                    f"Account Balance Request:\n"
                    f"The account number {masked_acc} could not be validated. Kindly verify your account number."
                )

        # 2. Credit Card Transactions Section
        if "CREDIT_CARD_USAGE" in api_results:
            res = api_results["CREDIT_CARD_USAGE"]
            masked_card = mask_card_number(entities.card_number or "")
            if res.get("status") == "SUCCESS":
                has_success = True
                txns = res.get("transactions", [])
                lines = [f"Credit Card Transactions ({masked_card}):"]
                if txns:
                    lines.append(f"Here is the summary of your last {len(txns)} transactions:")
                    for idx, t in enumerate(txns, 1):
                        lines.append(f"  {idx}. {t.get('date')} | {t.get('merchant')} | {mask_currency(t.get('amount'))} | Status: {t.get('status')}")
                else:
                    lines.append("No recent transactions found for the specified period.")
                sections["Credit Card Request"] = "\n".join(lines)
            else:
                has_failure = True
                sections["Credit Card Request"] = (
                    "Credit Card Request:\n"
                    "The credit card number provided could not be validated. Kindly recheck the card details and resend your request."
                )

        # 3. Bank Statement Section
        if "STATEMENT_REQUEST" in api_results:
            res = api_results["STATEMENT_REQUEST"]
            masked_acc = mask_account_number(entities.account_number or "")
            period = entities.statement_period or "Requested Period"
            if res.get("status") == "SUCCESS":
                has_success = True
                sections["Bank Statement"] = (
                    f"Bank Statement ({period}):\n"
                    f"• Account: {masked_acc}\n"
                    f"• Statement Reference ID: {res.get('statement_id')}\n"
                    f"• Download Link: {res.get('download_url')}\n"
                    f"Note: This link is protected with your NetBanking credentials."
                )
            else:
                has_failure = True
                sections["Bank Statement"] = (
                    f"Bank Statement Request ({period}):\n"
                    f"We could not retrieve the statement because the account number could not be validated. Please provide a valid 10-digit account number."
                )

        # Introductory tone adjustment
        if sentiment_res.is_urgent or sentiment_res.sentiment == SentimentType.URGENT:
            intro = "Thank you for reaching out. We understand the urgency of your query and have prioritized your request immediately."
        elif has_success and has_failure:
            intro = "We have partially processed your request. Please review the details below:"
        elif has_success:
            intro = "We have processed your request successfully."
        else:
            intro = "Thank you for contacting us. We encountered an issue while processing your request as outlined below:"

        body_parts = [greeting, "", intro, ""]
        for title, text in sections.items():
            body_parts.append(text)
            body_parts.append("")

        body_parts.append("Thank you,")
        body_parts.append(f"Customer Support Team\n{BANK_NAME}")
        body_parts.append(f"Toll-free: {SUPPORT_PHONE} | Email: {SUPPORT_EMAIL}")

        full_body = "\n".join(body_parts).strip()
        disclaimer = "CONFIDENTIAL: This automated response is generated by HDFC Bank's Secure Agentic AI System. Sensitive numbers have been masked in accordance with RBI and PCI-DSS guidelines."

        elapsed = (time.time() - start_time) * 1000
        log_audit_event(
            agent_name=self.name,
            step="DraftCustomerResponse",
            details={
                "has_success": has_success,
                "has_failure": has_failure,
                "sections_count": len(sections)
            },
            execution_time_ms=elapsed
        )

        return FinalEmailResponse(
            recipient_email=recipient_email,
            subject=f"{BANK_NAME} - Update on your request",
            greeting=greeting,
            sections=sections,
            full_email_body=full_body,
            masked_account_number=mask_account_number(entities.account_number or ""),
            masked_card_number=mask_card_number(entities.card_number or ""),
            has_partial_failure=(has_success and has_failure),
            sentiment_applied=sentiment_res.sentiment,
            disclaimer=disclaimer
        )

