# Low-Level Design (LLD) Document
## HDFC Bank - Intelligent Email Processing System

---

### 1. Package & Module Architecture
The codebase follows clean architecture principles with strict layer boundaries:

```
email_automation/
├── agents/             # Autonomous agent implementations (Single Responsibility)
│   ├── email_understanding_agent.py
│   ├── intent_sentiment_agent.py
│   ├── entity_extraction_agent.py
│   ├── validation_agent.py
│   ├── api_selection_agent.py
│   ├── response_generation_agent.py
│   └── audit_agent.py
├── apis/               # Mock core banking layer & MCP tool contracts
│   ├── mock_core_banking.py
│   ├── mcp_tools.py
│   └── dashboard.html
├── models/             # Strongly typed Pydantic V2 domain models
│   ├── schemas.py
│   └── llm_provider.py
├── prompts/            # Grounded system prompts & few-shot examples
│   └── templates.py
├── workflows/          # State orchestration graph & HITL risk governance
│   ├── state.py
│   ├── orchestrator.py
│   └── hitl_manager.py
├── utils/              # Cross-cutting concerns & compliance
│   ├── security_masker.py
│   ├── ocr_reader.py
│   ├── policy_rag.py
│   ├── language_detector.py
│   ├── omnichannel_adapter.py
│   └── logger.py
└── config/             # Environment & mock data store
    ├── settings.py
    └── mock_db.json
```

---

### 2. Class Diagram

```mermaid
classDiagram
    class BankingEmailOrchestrator {
        +EmailUnderstandingAgent email_agent
        +IntentSentimentAgent intent_sentiment_agent
        +EntityExtractionAgent entity_agent
        +ValidationAgent validation_agent
        +APISelectionAgent api_decision_agent
        +ResponseGenerationAgent response_agent
        +AuditLoggingAgent audit_agent
        +process_email(EmailInput email) WorkflowState
    }

    class WorkflowState {
        +str session_id
        +EmailInput email_input
        +str email_cleaned_text
        +str attachment_content
        +str detected_language
        +bool is_multilingual
        +IntentDetectionResult intent_result
        +SentimentAnalysisResult sentiment_result
        +ExtractedEntities extracted_entities
        +dict validation_results
        +list api_execution_plan
        +dict api_results
        +FinalEmailResponse final_response
        +float confidence_score
        +bool requires_human_approval
        +str approval_status
        +float total_latency_ms
    }

    class MockCoreBankingService {
        +validate_account(str acc) dict
        +validate_card(str card) dict
        +get_account_balance(str acc) dict
        +get_card_transactions(str card, int limit) dict
        +get_statement(str acc, str period) dict
    }

    class OllamaLLMProvider {
        +str base_url
        +str model
        +int timeout
        +check_connection() dict
        +complete(str prompt, str system_prompt) str
    }

    BankingEmailOrchestrator --> WorkflowState : mutates
    BankingEmailOrchestrator --> MockCoreBankingService : calls
    BankingEmailOrchestrator --> OllamaLLMProvider : infers
```

---

### 3. State Machine & Pipeline Transitions

```mermaid
stateDiagram-v2
    [*] --> INITIALIZED: Ingest EmailInput
    INITIALIZED --> PREPROCESSED: EmailUnderstandingAgent (Clean text, OCR, Language)
    PREPROCESSED --> CLASSIFIED: IntentSentimentAgent (Intents + Sentiment)
    CLASSIFIED --> EXTRACTED: EntityExtractionAgent (Account, Card, Dates)
    EXTRACTED --> VALIDATED: ValidationAgent (Core Banking Verification)
    
    state VALIDATED {
        [*] --> CheckStatus
        CheckStatus --> FullSuccess: All Credentials Valid
        CheckStatus --> PartialFailure: One Valid, One Invalid
        CheckStatus --> CriticalFailure: All Invalid
    }

    VALIDATED --> PLANNED: APISelectionAgent (DAG Execution Plan)
    PLANNED --> EXECUTED: Dispatch MCP Tool APIs
    EXECUTED --> DRAFTED: ResponseGenerationAgent (Apply PII Masking)
    
    state DecisionRisk {
        [*] --> CheckRisk
        CheckRisk --> FlagHITL: Urgency==True OR PartialFail==True
        CheckRisk --> AutoApprove: Standard Flow
    }

    DRAFTED --> DecisionRisk
    FlagHITL --> PENDING_APPROVAL: Push to HITL Manager Queue
    AutoApprove --> COMPLETED: AuditLoggingAgent
    PENDING_APPROVAL --> COMPLETED: Supervisor Approval
    COMPLETED --> [*]: Return Final WorkflowState
```

---

### 4. Core Agent Method Specifications

#### 4.1 `EmailUnderstandingAgent.process(email_input: EmailInput) -> Dict[str, Any]`
- **Input**: `EmailInput` (contains `body`, `attachment_paths`).
- **Logic**: Strips trailing carriage returns, collapses redundant whitespace, reads attachments via `extract_text_from_attachment()`, and detects query language.
- **Output**: Dictionary with `clean_body`, `attachment_text`, `combined_content`, `language`, `is_multilingual`.

#### 4.2 `IntentSentimentAgent.process(text: str) -> Tuple[IntentDetectionResult, SentimentAnalysisResult]`
- **Input**: Preprocessed combined email text.
- **Logic**: Sends prompt with strict JSON schema to `OllamaLLMProvider`. Determines whether single or multiple intents exist (`ACCOUNT_BALANCE`, `CREDIT_CARD_USAGE`, `STATEMENT_REQUEST`), and extracts emotional tone.
- **Output**: Structured `IntentDetectionResult` and `SentimentAnalysisResult`.

#### 4.3 `EntityExtractionAgent.process(text: str) -> ExtractedEntities`
- **Input**: Customer text + extracted attachment content.
- **Logic**: Performs regex and NER extraction for 10-digit account numbers, 16-digit card numbers (or masked `4567XXXX8901`), transaction limits, and calendar periods.
- **Output**: `ExtractedEntities` object.

#### 4.4 `ValidationAgent.process(entities: ExtractedEntities) -> Dict[str, Any]`
- **Input**: `ExtractedEntities`.
- **Logic**: Invokes `mock_core_banking.validate_account()` and `validate_card()`.
- **Output**: Dictionary mapping `account_validation` and `card_validation` to `AccountValidationResult` and `CardValidationResult`.

#### 4.5 `APISelectionAgent.plan_and_execute(intent_result, entities, validation_results) -> Dict[str, Any]`
- **Input**: Detected intents, entities, and validation outcomes.
- **Logic**: Builds a dependency execution plan. If an account is `VALID`, it schedules `GetAccountBalanceAPI` or `GetStatementAPI`. If a credit card is `INVALID`, it skips `GetCardTransactionsAPI` and flags partial failure.
- **Output**: Returns `api_execution_plan` and `api_results`.

#### 4.6 `ResponseGenerationAgent.draft_response(...) -> FinalEmailResponse`
- **Input**: Aggregated state including API results, validation flags, sentiment, and RAG policy lookup.
- **Logic**: Assembles official HDFC Bank response letter:
  - Formats balance in standard Indian currency format (`INR 1,25,000`).
  - Formats card transactions into structured bullet points.
  - Generates clear partial validation failure notices asking for card verification.
  - Masks all identifiers (`XXXX7890`, `4567XXXX8901`).
- **Output**: `FinalEmailResponse` schema.

---

### 5. Error Handling & Fault-Tolerance Strategy
1. **Network Timeouts & Offline Engine**: `OllamaLLMProvider` incorporates `OLLAMA_TIMEOUT` controls. If the local Ollama process is offline (`WinError 10061`), clear diagnostic messaging is provided.
2. **Missing Input Recovery**: If no account number is provided for a balance enquiry, the system generates a polite clarification request rather than crashing.
3. **Pure-Python Stream Fallback**: In minimal container environments without native C++ MuPDF binaries, `ocr_reader.py` falls back to pure-Python zlib stream decompression.


