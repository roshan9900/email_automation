# Assumptions and Limitations

## Assumptions
1. **Mock Core Banking**: As specified in Section 14 of the case study, core banking systems are simulated with a JSON-backed data store (`config/mock_db.json`).
2. **Simplified Authentication**: Identity matching is derived from verified email sender and presence of valid account credentials.
3. **No Real Banking Data**: All customer identities, card numbers, and balances are synthetic demonstration records.
4. **Offline Evaluation Guarantee**: The system provides an out-of-the-box Hybrid SLM rule-guided provider so reviewers can run and test the complete pipeline immediately without needing paid API keys or local daemon setup, while fully allowing live LLaMA 3 integration via standard environment variables.

## Limitations
1. **Email Protocol Gateway**: The system exposes REST and CLI runners. Direct production IMAP/SMTP polling requires an operational mail server exchange.
2. **Two-Factor Authentication**: For live high-risk account modifications or financial transfers, out-of-band OTP / NetBanking authorization would be required.
3. **Complex Multi-Page OCR**: The built-in attachment reader processes PDFs and plain-text/mock image attachments using PyMuPDF; advanced handwritten cheque OCR in production would incorporate fine-tuned vision models.

