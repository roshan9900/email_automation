# Agent Workflow & Orchestration Document

## Orchestration Lifecycle

1. **Email Ingestion**:
   - The user/system submits an `EmailInput` payload containing subject, sender, body, and attachment paths.
2. **Text Normalization & OCR**:
   - `EmailUnderstandingAgent` cleans whitespace, parses headers, and extracts PDF/scanned cheque attachments via `ocr_reader.py`.
3. **Intent & Sentiment Detection**:
   - `IntentSentimentAgent` performs classification across banking intent taxonomy (`ACCOUNT_BALANCE`, `CREDIT_CARD_USAGE`, `STATEMENT_REQUEST`, etc.).
   - Assesses sentiment urgency (`NEUTRAL`, `POSITIVE`, `NEGATIVE`, `URGENT`).
4. **Entity Extraction**:
   - `EntityExtractionAgent` isolates 10-digit account numbers, masked/unmasked card numbers, requested transaction counts, and statement calendar periods.
5. **Backend Verification**:
   - `ValidationAgent` queries `ValidateAccountAPI` and `ValidateCardAPI`.
6. **API Selection & Tool Invocation**:
   - `APISelectionAgent` identifies needed APIs, checks for dependencies, and invokes MCP tool handlers.
7. **Response Drafting & Redaction**:
   - `ResponseGenerationAgent` formats the reply, masks sensitive digits (e.g. `XXXX7890`), applies partial failure notes, and adds regulatory disclaimers.
8. **Audit Logging**:
   - `AuditLoggingAgent` records the transaction hash, decision route, latency, and status in `logs/audit.log`.

