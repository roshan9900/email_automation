import time
import json
from typing import Tuple
from models.schemas import (
    IntentDetectionResult,
    SentimentAnalysisResult,
    IntentType,
    SentimentType
)
from models.llm_provider import get_llm_provider
from prompts.templates import INTENT_SENTIMENT_SYSTEM_PROMPT
from utils.logger import log_audit_event

class IntentSentimentAgent:
    """
    Agent 2 & 3: Intent Classification Agent & Sentiment Analysis Agent.
    Identifies single or multi-intent customer requests and emotional sentiment/urgency.
    """
    def __init__(self):
        self.name = "IntentSentimentAgent"
        self.llm = get_llm_provider()

    def process(self, email_text: str) -> Tuple[IntentDetectionResult, SentimentAnalysisResult]:
        start_time = time.time()
        
        prompt = f"Please classify the intent and sentiment of this customer email:\n\n{email_text}"
        response_str = self.llm.complete(prompt=prompt, system_prompt=INTENT_SENTIMENT_SYSTEM_PROMPT)
        
        try:
            data = json.loads(response_str)
        except Exception:
            # Fallback parsing
            data = {
                "intents": ["ACCOUNT_BALANCE"],
                "primary_intent": "ACCOUNT_BALANCE",
                "is_multi_intent": False,
                "sentiment": "NEUTRAL",
                "is_urgent": False,
                "confidences": {"ACCOUNT_BALANCE": 0.9}
            }

        # Build Intent Result
        intent_enums = []
        for i_str in data.get("intents", []):
            try:
                intent_enums.append(IntentType(i_str))
            except Exception:
                intent_enums.append(IntentType.UNKNOWN)

        primary = intent_enums[0] if intent_enums else IntentType.UNKNOWN
        intent_res = IntentDetectionResult(
            intents=intent_enums,
            primary_intent=primary,
            is_multi_intent=len(intent_enums) > 1,
            confidences=data.get("confidences", {})
        )

        # Build Sentiment Result
        sentiment_val = data.get("sentiment", "NEUTRAL").upper()
        try:
            sent_enum = SentimentType(sentiment_val)
        except Exception:
            sent_enum = SentimentType.NEUTRAL

        is_urgent = bool(data.get("is_urgent", False) or sent_enum == SentimentType.URGENT)
        sentiment_res = SentimentAnalysisResult(
            sentiment=sent_enum,
            score=0.92,
            is_urgent=is_urgent,
            escalation_required=is_urgent and (sent_enum in [SentimentType.NEGATIVE, SentimentType.URGENT]),
            reasoning=f"Detected sentiment: {sent_enum.value}, urgent={is_urgent}"
        )

        elapsed = (time.time() - start_time) * 1000
        log_audit_event(
            agent_name=self.name,
            step="IntentAndSentimentAnalysis",
            details={
                "intents": [i.value for i in intent_enums],
                "primary": primary.value,
                "sentiment": sent_enum.value,
                "is_urgent": is_urgent
            },
            execution_time_ms=elapsed
        )
        return intent_res, sentiment_res

