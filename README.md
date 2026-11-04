# HDFC Bank - Intelligent Email Processing & Automated Customer Response System with MCP

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Agentic%20AI%20%2F%20MCP-purple.svg)]()
[![Compliance](https://img.shields.io/badge/Security-PCI--DSS%20%26%20PII%20Masked-green.svg)]()

Production-ready implementation of **Task - 1002: Intelligent Email Processing & Automated Customer Response System with MCP** for HDFC Bank.

---

## 1. Executive Summary & Problem Statement

Financial institutions receive thousands of customer emails daily concerning:
- Savings & current account balance inquiries
- Credit card usage and recent transaction statements
- Monthly bank statement requests
- Compound multi-intent requests within a single email thread
- Inquiries accompanied by document attachments (PDFs, scanned cheques, etc.)

Currently, support teams manually read emails, identify sentiment, validate account credentials, toggle between disparate core banking windows, and draft responses. This process is time-consuming, prone to human error, and lacks 24/7 scalability.

This system delivers an **AI-powered Agentic Automation Pipeline** leveraging:
- **Agentic AI Architecture** with 7 specialized agents
- **Model Context Protocol (MCP)** tool definitions for core banking integration
- **Multi-Intent & Sentiment Analysis** (with urgency and fraud escalation detection)
- **Automated PII/PCI Data Masking** (e.g., `XXXX7890`)
- **Robust Partial Failure Handling** (validating accounts and credit cards independently)

---

## 2. Solution Architecture & Agentic Workflow

```
Incoming Customer Email (Body + Optional Attachments)
                    │
                    ▼
       ┌─────────────────────────┐
       │ EmailUnderstandingAgent │ ◄── Attachment OCR / PDF Text Extraction
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │   IntentSentimentAgent  │ ◄── Multi-Intent & Sentiment Classification
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │ EntityExtractionAgent   │ ◄── Extracts Account, Card, Dates, Count
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │     ValidationAgent     │ ◄── Validates against Core Banking Records
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │   APISelectionAgent     │ ◄── API Decision Engine (Plans execution sequence)
       └────────────┬────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   [Core Banking APIs]   [Failure Routing]
   • GetAccountBalance    • Invalid card notice
   • GetCardTransactions  • Verification request
   • GetStatement
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │ ResponseGenerationAgent │ ◄── PII Masker (e.g., XXXX7890) & Tone Calibration
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │    AuditLoggingAgent    │ ◄── Audit trail logged to logs/audit.log
       └────────────┬────────────┘
                    │
                    ▼
         Final Email Response
```

---

## 3. Specialized Agents & Responsibilities

| Agent Name | Module | Responsibility |
| :--- | :--- | :--- |
| **Email Understanding Agent** | `agents/email_understanding_agent.py` | Sanitizes email text, extracts content from attachments (PDFs/Images) via PyMuPDF/OCR. |
| **Intent & Sentiment Agent** | `agents/intent_sentiment_agent.py` | Detects single/multiple intents and flags emotional tone (`NEUTRAL`, `POSITIVE`, `NEGATIVE`, `URGENT`). |
| **Entity Extraction Agent** | `agents/entity_extraction_agent.py` | Extracts account numbers, credit card numbers, statement periods, and transaction limits. |
| **Validation Agent** | `agents/validation_agent.py` | Cross-checks account/card validity against core banking mock data. |
| **API Selection Agent** | `agents/api_selection_agent.py` | Decision engine determining which APIs to execute, parallel dependencies, and MCP tool dispatch. |
| **Response Generation Agent** | `agents/response_generation_agent.py` | Assembles cohesive, professional response letters with partial success handling and PII masking. |
| **Audit & Logging Agent** | `agents/audit_agent.py` | Logs execution traces, step latencies, decision parameters, and compliance records. |

---

## 4. Business Scenarios Handled

### Scenario 1 – Account Balance Enquiry
- **Input**: `"Please provide my savings account balance for account number 1234567890."`
- **Output**: Masks account to `XXXX7890`, calls `GetAccountBalanceAPI`, and returns available balance `INR 1,25,000`.

### Scenario 2 – Credit Card Usage Enquiry
- **Input**: `"Please share my last 5 credit card transactions for card 4567XXXX8901."`
- **Output**: Validates card, queries `GetCardTransactionsAPI(limit=5)`, and outputs formatted transaction table with merchant names, dates, amounts, and statuses.

### Scenario 3 – Statement Request
- **Input**: `"Kindly send my bank statement for April 2026."`
- **Output**: Identifies period `April 2026`, retrieves or generates secure statement download URL and statement ID.

### Scenario 4 – Multiple Requests in Single Email
- **Input**: `"Please share my account balance for account 1234567890 and also send last 3 transactions of my credit card 987654321."`
- **Output**: Detects multiple intents, validates both credentials, fetches balance and card history concurrently, and consolidates findings into a single unified customer response.

### Scenario 5 – Partial Validation Failure
- **Input**: `"Please provide balance for account 1234567890 and card transactions for card 999999999."`
- **Outcome**: Account is valid; card is invalid.
- **Output**: Successfully returns the account balance, politely informs the customer that the card number was not recognized, and invites them to verify and resubmit card details.

---

## 5. Model Context Protocol (MCP) Tool Contracts

The system defines formal MCP tools in `apis/mcp_tools.py`:

```json
{
  "name": "ValidateAccountAPI",
  "description": "Validates whether the customer account number is active and authorized.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "account_number": { "type": "string" }
    },
    "required": ["account_number"]
  }
}
```

Other MCP tools include:
- `ValidateCardAPI`: `{"card_number": "string"}`
- `GetAccountBalanceAPI`: `{"account_number": "string"}`
- `GetCardTransactionsAPI`: `{"card_number": "string", "limit": "integer"}`
- `GetStatementAPI`: `{"account_number": "string", "period": "string"}`

---

## 6. Project Directory Structure

```text
email_automation/
├── CustomerEnquiry_AutomationTask1002.pdf   # Original Case Study Specification
├── config/
│   ├── settings.py                         # Config constants, thresholds, paths
│   └── mock_db.json                        # Pre-seeded customer profiles & cards
├── apis/
│   ├── mock_core_banking.py                # Simulated Core Banking Service
│   └── mcp_tools.py                        # MCP Tool definitions and dispatcher
├── models/
│   ├── schemas.py                          # Pydantic schemas for all entities & responses
│   └── llm_provider.py                     # LLaMA 3 / Groq / Ollama / Hybrid SLM provider
├── prompts/
│   └── templates.py                        # Standardized prompt instructions
├── agents/
│   ├── email_understanding_agent.py        # Text preprocessing & attachment handling
│   ├── intent_sentiment_agent.py           # Multi-intent & sentiment classification
│   ├── entity_extraction_agent.py          # Banking NER
│   ├── validation_agent.py                 # Account & card validation
│   ├── api_selection_agent.py              # API Decision Engine
│   ├── response_generation_agent.py        # Customer response drafter
│   └── audit_agent.py                      # Audit and compliance tracker
├── workflows/
│   ├── state.py                            # State dataclass for pipeline execution
│   └── orchestrator.py                     # Main orchestrator pipeline
├── utils/
│   ├── security_masker.py                  # PII & PCI compliance masking (XXXX7890)
│   ├── ocr_reader.py                       # Attachment reader (PDF/Image)
│   └── logger.py                           # Structured file & console logger
├── tests/
│   ├── test_scenarios.py                   # Pytest test cases covering Scenarios 1–6
│   └── sample_emails.json                  # Reusable test email corpus
├── logs/
│   └── audit.log                           # Audit trail of API executions and decisions
├── main.py                                 # Demonstration & interactive CLI runner
├── requirements.txt                        # Dependency manifest
└── README.md                               # Project documentation
```

---

## 7. Setup & Execution Instructions

### Installation

```powershell
cd "c:\Users\Roshan Salunke\Downloads\mediap\classrag\crisil\email_automation"
pip install -r requirements.txt
```

### Running the Case Study Demonstration (All 5 Scenarios)

```powershell
python main.py
```

### Running the Automated Pytest Suite

```powershell
pytest tests/test_scenarios.py -v
```

### Running Interactive Mode (Test any custom email)

```powershell
python main.py --interactive
```

### Starting the MCP API Server (Optional)

```powershell
python main.py --serve
```

---

## 8. Assumptions & Limitations

1. **Simulated Core Banking**: In accordance with Section 14 of the case study, core banking transactions are executed against an in-memory/JSON mock database with pre-configured accounts.
2. **Simplified Authentication**: Customer authentication is derived from sender email matching and credential presence. In a full production deployment, 2-Factor Authentication (OTP / NetBanking login magic link) would precede sensitive data dispatch.
3. **LLM Provider Agnostic**: The system defaults to an offline-capable, deterministic Hybrid SLM provider to guarantee immediate test execution without external API keys or network latency, while fully supporting hot-swapping to **LLaMA 3** via Groq or Ollama by setting `LLM_PROVIDER=groq` and `GROQ_API_KEY=...` in `.env`.
4. **Security & Privacy**: No raw card or full account numbers are ever sent to end-users or recorded in unmasked plain text within audit logs.

