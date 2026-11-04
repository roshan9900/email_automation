import time
import re
from typing import Dict, Any
from models.schemas import EmailInput
from utils.ocr_reader import extract_text_from_attachment
from utils.logger import log_audit_event

class EmailUnderstandingAgent:
    """
    Agent 1: Responsible for reading email content, cleaning/preprocessing text,
    and reading attachments via OCR.
    """
    def __init__(self):
        self.name = "EmailUnderstandingAgent"

    def process(self, email_input: EmailInput) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Clean email body text
        raw_body = email_input.body
        # Normalize whitespace and strip disclaimers/signatures if present
        clean_body = re.sub(r"\r\n", "\n", raw_body).strip()
        clean_body = re.sub(r"[ \t]+", " ", clean_body)

        # 2. Process attachments if provided
        attachment_texts = []
        for att_path in email_input.attachment_paths:
            extracted = extract_text_from_attachment(att_path)
            if extracted:
                attachment_texts.append(extracted)

        combined_text = clean_body
        if attachment_texts:
            combined_text += "\n\n[Attachment Content]:\n" + "\n".join(attachment_texts)

        elapsed = (time.time() - start_time) * 1000
        result = {
            "clean_body": clean_body,
            "attachment_text": "\n".join(attachment_texts),
            "combined_content": combined_text,
            "has_attachments": len(email_input.attachment_paths) > 0
        }
        
        log_audit_event(
            agent_name=self.name,
            step="EmailPreprocessing",
            details={"email_id": email_input.email_id, "has_attachments": result["has_attachments"]},
            execution_time_ms=elapsed
        )
        return result

