from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from models.schemas import (
    EmailInput,
    IntentDetectionResult,
    SentimentAnalysisResult,
    ExtractedEntities,
    FinalEmailResponse
)

class WorkflowState(BaseModel):
    session_id: str
    email_input: EmailInput
    email_cleaned_text: Optional[str] = None
    attachment_content: Optional[str] = None
    detected_language: Optional[str] = "English"
    is_multilingual: bool = False
    
    intent_result: Optional[IntentDetectionResult] = None
    sentiment_result: Optional[SentimentAnalysisResult] = None
    extracted_entities: Optional[ExtractedEntities] = None
    
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    api_execution_plan: List[Dict[str, Any]] = Field(default_factory=list)
    api_results: Dict[str, Any] = Field(default_factory=dict)
    
    final_response: Optional[FinalEmailResponse] = None
    confidence_score: float = 0.95
    requires_human_approval: bool = False
    approval_status: str = "AUTO_APPROVED"
    risk_reasons: List[str] = Field(default_factory=list)
    policy_lookup: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    total_latency_ms: float = 0.0
    status: str = "INITIALIZED"

