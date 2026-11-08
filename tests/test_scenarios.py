import os
import sys
import unittest
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.schemas import EmailInput, IntentType, ValidationStatus, SentimentType
from workflows.orchestrator import BankingEmailOrchestrator
from apis.mock_core_banking import banking_service

class TestBankingEmailScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # In unit tests, use fast deterministic hybrid SLM provider
        # to verify all banking logic, schemas, APIs and agents instantly (< 2s)
        cls._prev_provider = os.environ.get("LLM_PROVIDER")
        os.environ["LLM_PROVIDER"] = "hybrid"

    @classmethod
    def tearDownClass(cls):
        if cls._prev_provider is not None:
            os.environ["LLM_PROVIDER"] = cls._prev_provider
        else:
            os.environ.pop("LLM_PROVIDER", None)

    def setUp(self):
        self.orchestrator = BankingEmailOrchestrator()

    def test_scenario_1_account_balance(self):
        """
        Scenario 1 – Account Balance Enquiry
        Customer Email: 'Please provide my savings account balance for account number 1234567890.'
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-1",
            sender="john.doe@example.com",
            subject="Balance Query",
            body="Please provide my savings account balance for account number 1234567890."
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertIn(IntentType.ACCOUNT_BALANCE, state.intent_result.intents)
        self.assertEqual(state.extracted_entities.account_number, "1234567890")
        self.assertEqual(state.validation_results["account_validation"].status, ValidationStatus.VALID)
        self.assertIn("ACCOUNT_BALANCE", state.api_results)
        self.assertEqual(state.api_results["ACCOUNT_BALANCE"]["balance"], 125000.0)
        
        # Verify response email content & masking
        resp_text = state.final_response.full_email_body
        self.assertIn("XXXX7890", resp_text)
        self.assertIn("INR 1,25,000", resp_text)

    def test_scenario_2_credit_card_usage(self):
        """
        Scenario 2 – Credit Card Usage Enquiry
        Customer Email: 'Please share my last 5 credit card transactions for card 4567XXXX8901.'
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-2",
            sender="john.doe@example.com",
            subject="Card Enquiry",
            body="Please share my last 5 credit card transactions for card 4567XXXX8901."
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertIn(IntentType.CREDIT_CARD_USAGE, state.intent_result.intents)
        self.assertIn("4567XXXX8901", state.extracted_entities.card_number)
        self.assertEqual(state.validation_results["card_validation"].status, ValidationStatus.VALID)
        self.assertIn("CREDIT_CARD_USAGE", state.api_results)
        self.assertEqual(len(state.api_results["CREDIT_CARD_USAGE"]["transactions"]), 5)
        
        resp_text = state.final_response.full_email_body
        self.assertTrue("Amazon India" in resp_text or "Swiggy" in resp_text)

    def test_scenario_3_statement_request(self):
        """
        Scenario 3 – Statement Request
        Customer Email: 'Kindly send my bank statement for April 2026.'
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-3",
            sender="john.doe@example.com",
            subject="Statement Request",
            body="Kindly send my bank statement for April 2026 for account 1234567890."
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertIn(IntentType.STATEMENT_REQUEST, state.intent_result.intents)
        self.assertEqual(state.extracted_entities.statement_period, "April 2026")
        self.assertIn("STATEMENT_REQUEST", state.api_results)
        self.assertEqual(state.api_results["STATEMENT_REQUEST"]["status"], "SUCCESS")
        
        resp_text = state.final_response.full_email_body
        self.assertTrue("STMT-202604-1234567890" in resp_text or "STMT" in resp_text)
        self.assertIn("https://", resp_text)

    def test_scenario_4_multiple_requests(self):
        """
        Scenario 4 – Multiple Requests in One Email
        Customer Email: 'Please share my account balance for account 1234567890 and also send last 3 transactions of my credit card 987654321.'
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-4",
            sender="john.doe@example.com",
            subject="Multi-Request",
            body="Please share my account balance for account 1234567890 and also send last 3 transactions of my credit card 987654321."
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertTrue(state.intent_result.is_multi_intent)
        self.assertIn(IntentType.ACCOUNT_BALANCE, state.intent_result.intents)
        self.assertIn(IntentType.CREDIT_CARD_USAGE, state.intent_result.intents)
        
        # Both APIs must be called
        self.assertIn("ACCOUNT_BALANCE", state.api_results)
        self.assertIn("CREDIT_CARD_USAGE", state.api_results)
        self.assertEqual(state.api_results["ACCOUNT_BALANCE"]["balance"], 125000.0)
        self.assertEqual(len(state.api_results["CREDIT_CARD_USAGE"]["transactions"]), 3)

        resp_text = state.final_response.full_email_body
        self.assertIn("Account Balance", resp_text)
        self.assertIn("Credit Card", resp_text)

    def test_scenario_5_partial_validation_failure(self):
        """
        Scenario 5 – Partial Validation Failure
        Customer Email: 'Please provide balance for account 1234567890 and card transactions for card 999999999.'
        Account valid, card invalid.
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-5",
            sender="john.doe@example.com",
            subject="Balance and Card Check",
            body="Please provide balance for account 1234567890 and card transactions for card 999999999."
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertTrue(state.final_response.has_partial_failure)
        self.assertEqual(state.validation_results["account_validation"].status, ValidationStatus.VALID)
        self.assertEqual(state.validation_results["card_validation"].status, ValidationStatus.INVALID)
        
        resp_text = state.final_response.full_email_body
        self.assertIn("XXXX7890", resp_text)
        self.assertIn("INR 1,25,000", resp_text)
        self.assertIn("could not be validated", resp_text)
        self.assertIn("recheck the card details", resp_text)

    def test_scenario_6_urgent_escalation(self):
        """
        Scenario 6 – Urgent Escalation
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-6",
            sender="john.doe@example.com",
            subject="URGENT FRAUD ALERT",
            body="URGENT: I see an unauthorized charge on card 4567XXXX8901. Please check transactions immediately!"
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertTrue(state.sentiment_result.is_urgent)
        self.assertIn(state.final_response.sentiment_applied, [SentimentType.URGENT, SentimentType.NEGATIVE])
        self.assertIn("prioritized your request", state.final_response.full_email_body)

    def test_scenario_7_attachment_ocr(self):
        """
        Scenario 7 – OCR Attachment Processing (Section 13 Optional Enhancement)
        """
        pdf_path = CURRENT_DIR / "tests" / "test_cheque_attachment.pdf"
        email = EmailInput(
            email_id="TEST-SCENARIO-7-OCR",
            sender="john.doe@example.com",
            subject="Attached Cheque Record Query",
            body="Please see my attached document and share my account balance.",
            attachment_paths=[str(pdf_path)]
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        self.assertTrue(len(state.attachment_content) > 0)
        self.assertIn("1234567890", state.attachment_content)
        self.assertEqual(state.extracted_entities.account_number, "1234567890")
        self.assertEqual(state.validation_results["account_validation"].status, ValidationStatus.VALID)

    def test_scenario_8_rag_policy_and_hitl(self):
        """
        Scenario 8 – RAG Policy Knowledge Lookup & Human-in-the-Loop Risk Flagging
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-8-HITL",
            sender="john.doe@example.com",
            subject="Urgent Fraud Question",
            body="URGENT: Someone made an unauthorized transaction on my card 4567XXXX8901. What is your liability policy?"
        )
        state = self.orchestrator.process_email(email)
        
        self.assertEqual(state.status, "SUCCESS")
        # HITL Flagged
        self.assertTrue(state.requires_human_approval)
        self.assertEqual(state.approval_status, "PENDING_APPROVAL")
        # RAG Policy Enriched
        self.assertIsNotNone(state.policy_lookup)
        self.assertIn("Zero Liability", state.policy_lookup["topic"])
        self.assertIn("Zero Liability", state.final_response.full_email_body)

    def test_scenario_9_ollama_provider_check(self):
        """
        Scenario 9 – Tests Ollama LLM provider structure and diagnostic health probe
        """
        from models.llm_provider import OllamaLLMProvider
        provider = OllamaLLMProvider()
        conn = provider.check_connection()
        self.assertIn("online", conn)
        self.assertIn("target_model", conn)

    def test_scenario_10_multilingual_support(self):
        """
        Scenario 10 – Multi-Language Enquiry Support (Section 13 Optional Enhancement)
        Customer writes in Hindi / Hinglish: 'Namaste, kripya mera savings account balance bataye for 1234567890.'
        """
        email = EmailInput(
            email_id="TEST-SCENARIO-10-LANG",
            sender="rohit.sharma@example.com",
            subject="Khata Balance Jaankari",
            body="Namaste, kripya mera savings account balance bataye for account number 1234567890. Dhanyawad."
        )
        state = self.orchestrator.process_email(email)
        self.assertEqual(state.status, "SUCCESS")
        self.assertTrue(state.is_multilingual)
        self.assertIn("Hindi", state.detected_language)
        self.assertEqual(state.extracted_entities.account_number, "1234567890")
        self.assertEqual(state.api_results["ACCOUNT_BALANCE"]["balance"], 125000.0)

    def test_scenario_11_omnichannel_voice_ivr(self):
        """
        Scenario 11 – Omnichannel Voice / IVR Call Simulation (Section 13 Optional Enhancement)
        Customer calls Phone Banking IVR and asks for account balance via voice.
        """
        from utils.omnichannel_adapter import OmnichannelAdapter
        adapter = OmnichannelAdapter(orchestrator=self.orchestrator)
        transcript = "Hi, I am calling to check my savings account balance for account 1234567890."
        res = adapter.process_voice_call(
            voice_transcript=transcript,
            caller_phone="+91-9876543210",
            registered_email="john.doe@example.com"
        )
        self.assertEqual(res["channel"], "OMNICHANNEL_VOICE_IVR")
        self.assertIn("Rupees 125,000", res["ivr_voice_script"])
        self.assertIn("XXXX7890", res["email_response_body"])

if __name__ == "__main__":
    unittest.main()
