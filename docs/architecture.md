# Solution Architecture Document: HDFC Bank Intelligent Email Processing System

## 1. System Overview
The Intelligent Email Processing System is designed to automate customer inquiry handling for HDFC Bank using an **Agentic AI architecture** integrated with **Model Context Protocol (MCP)** banking tool specifications.

## 2. High-Level Architectural Flow
```
[ Incoming Customer Email ]
           │
           ▼
[ Email Understanding Agent ] ── (OCR & Attachment Extraction)
           │
           ▼
[ Intent & Sentiment Agent ]  ── (Multi-Intent Classification & Escalation Scoring)
           │
           ▼
[ Entity Extraction Agent ]   ── (Account, Card, Limit, Date Parsing)
           │
           ▼
[ Validation Agent ]          ── (Pre-execution validation against Core Banking)
           │
           ▼
[ API Decision Engine ]       ── (MCP Tool Orchestration & Dependency Sequencing)
           │
           ▼
[ Mock Core Banking APIs ]    ── (Balance, Transactions, Statements)
           │
           ▼
[ Response Generation Agent ] ── (PCI/PII Masking & Tone Calibration)
           │
           ▼
[ Final Customer Email ] + [ Audit Trail in logs/audit.log ]
```

## 3. Architecture Principles
1. **Decoupled Agent Specialization**: Each agent has single-responsibility domain boundaries (Email Understanding, Intent/Sentiment, NER, Validation, Decision, Generation, Audit).
2. **Security & Privacy First**: Under no circumstances are raw account numbers or credit card numbers exposed in generated customer letters or plain-text audit logs (enforced via `utils/security_masker.py`).
3. **Resilience & Partial Failure Handling**: In multi-intent queries where one credential is valid and another is invalid, valid requests are processed while invalid items are diplomatically requested for customer resubmission.
4. **Model Context Protocol (MCP) Standards**: Standardized JSON-schema tool interfaces decoupling LLM planning from core banking execution.

