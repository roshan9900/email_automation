from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SentimentType(str, Enum):
    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    URGENT = "URGENT"

class IntentType(str, Enum):
    ACCOUNT_BALANCE = "ACCOUNT_BALANCE"
    CREDIT_CARD_USAGE = "CREDIT_CARD_USAGE"
    STATEMENT_REQUEST = "STATEMENT_REQUEST"
    GENERAL_ENQUIRY = "GENERAL_ENQUIRY"
    UNKNOWN = "UNKNOWN"

class EmailInput(BaseModel):
    email_id: Optional[str] = "EMAIL-001"
    sender: str = "customer@example.com"
    subject: str = "Customer Enquiry"
    body: str
    attachment_paths: List[str] = Field(default_factory=list)

class SentimentAnalysisResult(BaseModel):
    sentiment: SentimentType = SentimentType.NEUTRAL
    score: float = 0.8
    is_urgent: bool = False
    escalation_required: bool = False
    reasoning: str = ""

class ExtractedEntities(BaseModel):
    account_number: Optional[str] = None
    card_number: Optional[str] = None
    transaction_count: Optional[int] = None
    statement_period: Optional[str] = None
    customer_name: Optional[str] = None
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

class IntentDetectionResult(BaseModel):
    intents: List[IntentType] = Field(default_factory=list)
    primary_intent: IntentType = IntentType.UNKNOWN
    is_multi_intent: bool = False
    confidences: Dict[str, float] = Field(default_factory=dict)

class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    ERROR = "ERROR"

class AccountValidationResult(BaseModel):
    status: ValidationStatus
    account_number: str
    customer_name: Optional[str] = None
    account_type: Optional[str] = None
    error_message: Optional[str] = None

class CardValidationResult(BaseModel):
    status: ValidationStatus
    card_number: str
    card_type: Optional[str] = None
    card_holder: Optional[str] = None
    error_message: Optional[str] = None

class AccountBalanceResult(BaseModel):
    status: str
    account_number: str
    balance: Optional[float] = None
    currency: Optional[str] = "INR"
    account_type: Optional[str] = None
    error_message: Optional[str] = None

class TransactionItem(BaseModel):
    id: str
    date: str
    merchant: str
    amount: float
    type: str
    status: str

class CardTransactionsResult(BaseModel):
    status: str
    card_number: str
    transactions: List[TransactionItem] = Field(default_factory=list)
    total_returned: int = 0
    error_message: Optional[str] = None

class StatementResult(BaseModel):
    status: str
    account_number: str
    period: str
    statement_id: Optional[str] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None

class ExecutionStepResult(BaseModel):
    api_name: str
    endpoint: str
    request_params: Dict[str, Any]
    response_data: Dict[str, Any]
    status_code: int = 200
    latency_ms: float = 0.0
    success: bool = True

class FinalEmailResponse(BaseModel):
    recipient_email: str
    subject: str
    greeting: str
    sections: Dict[str, str] = Field(default_factory=dict)
    full_email_body: str
    masked_account_number: Optional[str] = None
    masked_card_number: Optional[str] = None
    has_partial_failure: bool = False
    sentiment_applied: SentimentType = SentimentType.NEUTRAL
    disclaimer: str = ""

