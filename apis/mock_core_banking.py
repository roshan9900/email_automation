import json
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import DATA_FILE
from models.schemas import (
    ValidationStatus,
    AccountValidationResult,
    CardValidationResult,
    AccountBalanceResult,
    CardTransactionsResult,
    StatementResult,
    TransactionItem
)

class MockCoreBankingService:
    """
    Mock Core Banking Service simulating HDFC Bank's core banking applications
    for Account and Credit Card management.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATA_FILE
        self._load_db()

    def _load_db(self):
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        else:
            self.db = {"accounts": {}, "credit_cards": {}}

    def validate_account(self, account_number: str) -> AccountValidationResult:
        """
        ValidateAccountAPI: Checks whether the account number exists and is active.
        """
        self._load_db()
        clean_acc = account_number.strip().replace(" ", "")
        account = self.db.get("accounts", {}).get(clean_acc)
        
        if account and account.get("status") == "ACTIVE":
            return AccountValidationResult(
                status=ValidationStatus.VALID,
                account_number=clean_acc,
                customer_name=account.get("customer_name"),
                account_type=account.get("account_type")
            )
        
        return AccountValidationResult(
            status=ValidationStatus.INVALID,
            account_number=clean_acc,
            error_message=f"Account number '{clean_acc}' was not found or is inactive in core banking records."
        )

    def validate_card(self, card_number: str) -> CardValidationResult:
        """
        ValidateCardAPI: Validates credit card number against active cards.
        Supports masked format (4567XXXX8901) and unmasked format.
        """
        self._load_db()
        clean_card = card_number.strip().replace(" ", "").replace("-", "")
        cards_dict = self.db.get("credit_cards", {})

        # Direct match or partial masked match
        matched_card = None
        for key, val in cards_dict.items():
            if key == clean_card or val.get("full_card_number") == clean_card or val.get("card_number") == clean_card:
                matched_card = val
                break
            # Match last 4 digits if masked input provided
            if "X" in clean_card.upper() and clean_card.upper().endswith(key[-4:]):
                matched_card = val
                break

        if matched_card and matched_card.get("status") == "ACTIVE":
            return CardValidationResult(
                status=ValidationStatus.VALID,
                card_number=card_number,
                card_type=matched_card.get("card_type"),
                card_holder=matched_card.get("customer_name")
            )

        return CardValidationResult(
            status=ValidationStatus.INVALID,
            card_number=card_number,
            error_message=f"Credit card '{card_number}' could not be verified in core records."
        )

    def get_account_balance(self, account_number: str) -> AccountBalanceResult:
        """
        GetAccountBalanceAPI: Fetches current balance for an account.
        """
        val = self.validate_account(account_number)
        if val.status != ValidationStatus.VALID:
            return AccountBalanceResult(
                status="FAILED",
                account_number=account_number,
                error_message=val.error_message
            )

        account = self.db["accounts"][account_number.strip()]
        return AccountBalanceResult(
            status="SUCCESS",
            account_number=account_number,
            balance=account.get("balance"),
            currency=account.get("currency", "INR"),
            account_type=account.get("account_type")
        )

    def get_card_transactions(self, card_number: str, limit: int = 5) -> CardTransactionsResult:
        """
        GetCardTransactionsAPI: Fetches the last N transactions for a credit card.
        """
        val = self.validate_card(card_number)
        if val.status != ValidationStatus.VALID:
            return CardTransactionsResult(
                status="FAILED",
                card_number=card_number,
                error_message=val.error_message
            )

        # Retrieve card record
        cards_dict = self.db.get("credit_cards", {})
        matched_card = None
        clean_card = card_number.strip().replace(" ", "").replace("-", "")
        for key, card in cards_dict.items():
            if key == clean_card or card.get("card_number") == clean_card or (
                "X" in clean_card.upper() and clean_card.upper().endswith(key[-4:])
            ):
                matched_card = card
                break

        txns_raw = matched_card.get("transactions", [])[:limit]
        txns = [TransactionItem(**t) for t in txns_raw]
        return CardTransactionsResult(
            status="SUCCESS",
            card_number=card_number,
            transactions=txns,
            total_returned=len(txns)
        )

    def get_statement(self, account_number: str, period: str) -> StatementResult:
        """
        GetStatementAPI: Generates or retrieves bank statement for a specified period.
        """
        val = self.validate_account(account_number)
        if val.status != ValidationStatus.VALID:
            return StatementResult(
                status="FAILED",
                account_number=account_number,
                period=period,
                error_message=val.error_message
            )

        account = self.db["accounts"][account_number.strip()]
        statements = account.get("statements", {})
        
        # Exact or fuzzy month match
        stmt_data = None
        for p, data in statements.items():
            if period.lower() in p.lower() or p.lower() in period.lower():
                stmt_data = data
                break

        if stmt_data:
            return StatementResult(
                status="SUCCESS",
                account_number=account_number,
                period=period,
                statement_id=stmt_data.get("statement_id"),
                download_url=stmt_data.get("download_url")
            )
        
        # If not already archived, dynamically generate statement reference
        generated_id = f"STMT-{period.replace(' ', '').upper()}-{account_number[-4:]}"
        download_url = f"https://netbanking.hdfcbank.com/statements/{generated_id}.pdf"
        return StatementResult(
            status="SUCCESS",
            account_number=account_number,
            period=period,
            statement_id=generated_id,
            download_url=download_url
        )

# Global singleton
banking_service = MockCoreBankingService()

