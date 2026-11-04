# Low-Level Design (LLD) Document

## 1. Module Hierarchy
- `agents/`: Implementation of 7 distinct specialized agents.
- `apis/`: Core banking mock engine and MCP tool adapters.
- `models/`: Strongly-typed Pydantic domain schemas and LLM provider interfaces.
- `prompts/`: Role-specific prompts for zero-shot and few-shot reasoning.
- `workflows/`: Orchestrator state graph and end-to-end execution pipeline.
- `utils/`: PII masking, attachment extraction (OCR), and audit logger.

## 2. Key Data Models (`models/schemas.py`)
- `EmailInput`: `sender`, `subject`, `body`, `attachment_paths`
- `IntentDetectionResult`: `intents` (List of `IntentType`), `primary_intent`, `is_multi_intent`, `confidences`
- `SentimentAnalysisResult`: `sentiment` (`NEUTRAL`, `POSITIVE`, `NEGATIVE`, `URGENT`), `is_urgent`, `score`
- `ExtractedEntities`: `account_number`, `card_number`, `transaction_count`, `statement_period`
- `FinalEmailResponse`: `recipient_email`, `subject`, `full_email_body`, `masked_account_number`, `masked_card_number`, `has_partial_failure`

## 3. State Management
`WorkflowState` acts as the blackboard for all agents:
- Each agent receives the current state, processes its dedicated step, and updates state attributes.
- Latencies are captured per agent in milliseconds and recorded to `logs/audit.log`.

