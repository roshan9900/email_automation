"""
Omnichannel Adapter Module (Section 13 Optional Enhancement)
Bridges Voice/IVR inquiries, Phone Transcripts, and Email Automation Pipeline.
"""
from typing import Dict, Any, Optional
from models.schemas import EmailInput
from workflows.state import WorkflowState

class OmnichannelAdapter:
    """
    Adapter enabling seamless Omnichannel Banking support.
    Accepts speech-to-text transcripts from customer IVR / Phone banking,
    maps customer identity, triggers agentic processing, and generates
    both a detailed email confirmation and an audio-ready IVR voice script.
    """
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator

    def convert_voice_to_email_input(
        self,
        voice_transcript: str,
        caller_phone: str,
        caller_name: Optional[str] = "Customer",
        registered_email: Optional[str] = "john.doe@example.com"
    ) -> EmailInput:
        """
        Transforms a phone call transcription into a standardized EmailInput schema.
        """
        return EmailInput(
            email_id=f"VOICE-{abs(hash(caller_phone)) % 100000}",
            sender=registered_email,
            subject=f"[Phone Banking Enquiry - Ref {caller_phone[-4:]}]",
            body=voice_transcript
        )

    def generate_ivr_voice_response(self, state: WorkflowState) -> str:
        """
        Produces a concise, natural, SSML/Audio-friendly voice script for IVR read-out.
        """
        if not state.final_response:
            return "Thank you for calling HDFC Bank. We are processing your request."

        intents = state.intent_result.intents if state.intent_result else []
        voice_lines = ["Thank you for contacting HDFC Bank."]

        if state.final_response.has_partial_failure:
            voice_lines.append(
                "Your account balance was retrieved, but your card details could not be verified. "
                "A detailed summary has been sent to your registered email address."
            )
            return " ".join(voice_lines)

        if "ACCOUNT_BALANCE" in [i.value for i in intents]:
            bal_data = state.api_results.get("ACCOUNT_BALANCE", {})
            bal = bal_data.get("balance", 0)
            voice_lines.append(f"Your available savings account balance is Rupees {int(bal):,}.")

        if "CREDIT_CARD_USAGE" in [i.value for i in intents]:
            txn_data = state.api_results.get("CREDIT_CARD_USAGE", {})
            count = txn_data.get("total_returned", 0)
            voice_lines.append(f"Your recent {count} credit card transactions have been retrieved.")

        if "STATEMENT_REQUEST" in [i.value for i in intents]:
            voice_lines.append("Your account statement has been generated and sent to your email.")

        voice_lines.append("A full breakdown has been dispatched to your registered email. Have a great day!")
        return " ".join(voice_lines)

    def process_voice_call(
        self,
        voice_transcript: str,
        caller_phone: str,
        registered_email: str = "john.doe@example.com"
    ) -> Dict[str, Any]:
        """
        End-to-end voice processing: takes transcript, executes agent graph,
        and returns multichannel response bundle (Email + Voice TTS script).
        """
        email_input = self.convert_voice_to_email_input(
            voice_transcript=voice_transcript,
            caller_phone=caller_phone,
            registered_email=registered_email
        )
        state = self.orchestrator.process_email(email_input)
        voice_script = self.generate_ivr_voice_response(state)

        return {
            "channel": "OMNICHANNEL_VOICE_IVR",
            "caller_phone": caller_phone,
            "registered_email": registered_email,
            "session_id": state.session_id,
            "ivr_voice_script": voice_script,
            "email_response_body": state.final_response.full_email_body if state.final_response else "",
            "workflow_state": state
        }

