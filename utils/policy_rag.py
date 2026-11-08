import re
from typing import List, Dict, Any, Optional

# HDFC Bank Official Customer FAQ & Policy Repository
HDFC_BANK_POLICIES: List[Dict[str, Any]] = [
    {
        "id": "POL-001",
        "topic": "Minimum Average Balance (MAB)",
        "keywords": ["minimum balance", "mab", "penalty", "average balance", "charges", "savings account minimum"],
        "content": "For HDFC Regular Savings Accounts in Metro/Urban branches, the Minimum Average Monthly Balance (AMB) is INR 10,000. For Semi-Urban branches, it is INR 5,000. If the AMB is not maintained, a shortfall charge ranging from INR 150 to INR 600 + GST applies based on the shortfall percentage."
    },
    {
        "id": "POL-002",
        "topic": "Fraud & Unauthorized Transaction Zero Liability",
        "keywords": ["fraud", "unauthorized", "stolen card", "lost card", "suspicious", "scam", "dispute"],
        "content": "Under HDFC Bank Zero Liability Policy, if an unauthorized transaction is reported within 3 working days of receiving the SMS/email alert, the customer has zero liability. Report immediately by calling 1800-202-6161 or via NetBanking 'Hotlist Card' service."
    },
    {
        "id": "POL-003",
        "topic": "Credit Card Reward Points & Redemption",
        "keywords": ["reward points", "rewards", "cashback", "redeem points", "regalia points", "millennia"],
        "content": "HDFC Regalia Gold cardholders earn 4 reward points per INR 150 spent. Points can be redeemed for flights, hotels, and products on the SmartBuy portal (1 RP = up to INR 0.50). Reward points are valid for 24 months from the date of accrual."
    },
    {
        "id": "POL-004",
        "topic": "Account Statement Generation & Delivery",
        "keywords": ["statement fee", "duplicate statement", "physical statement", "email statement", "e-statement"],
        "content": "Monthly e-statements sent via email are 100% free of charge. Historical statements up to 5 years can be downloaded anytime free via NetBanking. Physical branch statements incur a nominal charge of INR 100 per request."
    },
    {
        "id": "POL-005",
        "topic": "Credit Card Billing & Interest-Free Period",
        "keywords": ["interest rate", "billing cycle", "due date", "grace period", "apr", "card payment"],
        "content": "HDFC Bank Credit Cards offer an interest-free grace period of up to 50 days from the start of the billing cycle. If the total amount due is paid on or before the payment due date, no interest is levied. Financing charges of 3.6% per month (43.2% per annum) apply on revolving balances."
    }
]

class BankingPolicyRAG:
    """
    RAG-based Banking Policy Knowledge Engine for HDFC Bank.
    Retrieves verified banking policies, regulatory disclaimers, and FAQs
    to enrich automated customer responses.
    """
    def __init__(self, policies: Optional[List[Dict[str, Any]]] = None):
        self.policies = policies or HDFC_BANK_POLICIES

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        query_tokens = set(re.findall(r"\w+", query.lower()))
        scored_policies = []

        for p in self.policies:
            score = 0
            # Keyword matching
            for kw in p["keywords"]:
                kw_tokens = set(re.findall(r"\w+", kw.lower()))
                overlap = len(query_tokens.intersection(kw_tokens))
                if overlap > 0:
                    score += overlap * 2.0
            
            # Content token overlap
            content_tokens = set(re.findall(r"\w+", p["content"].lower()))
            overlap_content = len(query_tokens.intersection(content_tokens))
            score += overlap_content * 0.1

            if score > 0:
                scored_policies.append((score, p))

        scored_policies.sort(key=lambda x: x[0], reverse=True)
        return [p for score, p in scored_policies[:top_k]]

# Singleton instance
policy_rag = BankingPolicyRAG()

