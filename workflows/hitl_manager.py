from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from models.schemas import SentimentType

class HITLReviewItem:
    def __init__(
        self,
        session_id: str,
        email_id: str,
        sender: str,
        subject: str,
        incoming_body: str,
        draft_response: str,
        confidence_score: float,
        risk_reasons: List[str],
        status: str = "PENDING_APPROVAL"
    ):
        self.session_id = session_id
        self.email_id = email_id
        self.sender = sender
        self.subject = subject
        self.incoming_body = incoming_body
        self.draft_response = draft_response
        self.confidence_score = confidence_score
        self.risk_reasons = risk_reasons
        self.status = status  # PENDING_APPROVAL, APPROVED, REJECTED, MODIFIED
        self.reviewer_notes: Optional[str] = None
        self.reviewed_at: Optional[str] = None
        self.created_at: str = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "email_id": self.email_id,
            "sender": self.sender,
            "subject": self.subject,
            "incoming_body": self.incoming_body,
            "draft_response": self.draft_response,
            "confidence_score": self.confidence_score,
            "risk_reasons": self.risk_reasons,
            "status": self.status,
            "reviewer_notes": self.reviewer_notes,
            "reviewed_at": self.reviewed_at,
            "created_at": self.created_at
        }

class HumanInTheLoopManager:
    """
    Human-in-the-Loop (HITL) Governance & Review Manager.
    Evaluates regulatory and operational risk on automated email drafts.
    Holds high-risk, low-confidence, or urgent emails for banking officer sign-off.
    """
    def __init__(self):
        self.review_queue: Dict[str, HITLReviewItem] = {}

    def evaluate_risk(
        self,
        sentiment: SentimentType,
        is_urgent: bool,
        has_partial_failure: bool,
        confidence_score: float,
        entities_found: bool
    ) -> Tuple[bool, List[str]]:
        reasons = []
        
        if is_urgent or sentiment == SentimentType.URGENT:
            reasons.append("Customer flagged URGENT / Potential Fraud or Escalation")
        if has_partial_failure:
            reasons.append("Partial Validation Failure detected (Card or Account mismatch)")
        if confidence_score < 0.80:
            reasons.append(f"Confidence score {confidence_score:.2f} below auto-dispatch threshold (0.80)")
        if not entities_found:
            reasons.append("No valid account or card entity extracted")

        requires_review = len(reasons) > 0
        return requires_review, reasons

    def add_to_queue(self, item: HITLReviewItem):
        self.review_queue[item.session_id] = item

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        return [
            item.to_dict()
            for item in self.review_queue.values()
            if item.status == "PENDING_APPROVAL"
        ]

    def approve(self, session_id: str, reviewer_notes: str = "Approved by Supervisor") -> Optional[Dict[str, Any]]:
        if session_id in self.review_queue:
            item = self.review_queue[session_id]
            item.status = "APPROVED"
            item.reviewer_notes = reviewer_notes
            item.reviewed_at = datetime.now().isoformat()
            return item.to_dict()
        return None

    def modify_and_approve(self, session_id: str, modified_draft: str, reviewer_notes: str) -> Optional[Dict[str, Any]]:
        if session_id in self.review_queue:
            item = self.review_queue[session_id]
            item.draft_response = modified_draft
            item.status = "MODIFIED"
            item.reviewer_notes = reviewer_notes
            item.reviewed_at = datetime.now().isoformat()
            return item.to_dict()
        return None

# Global HITL Singleton
hitl_manager = HumanInTheLoopManager()
