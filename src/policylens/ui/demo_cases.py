"""Pre-loaded demo use cases for the PolicyLens UI.

Four use cases designed to exercise different regulatory paths
and expose specific intentional gaps in the Meridian policies.
"""

from __future__ import annotations

DEMO_CASES: dict[str, str] = {
    "Credit Decisioning with Alternative Data": (
        "XGBoost credit decisioning model using utility payment and rent history "
        "as alternative data features. Model automates initial credit approval "
        "decisions for consumer lending."
    ),
    "Customer Service GenAI Chatbot": (
        "GPT-4 powered customer service chatbot handling account inquiries and "
        "providing financial product recommendations to retail banking customers."
    ),
    "Fraud Detection Ensemble Model": (
        "Real-time fraud detection ensemble model combining gradient boosting and "
        "neural network components for automated transaction scoring. Model makes "
        "autonomous block/allow decisions on consumer transactions with a 50ms "
        "latency requirement."
    ),
    "Internal Document Summarization Tool": (
        "Internal-only document summarization tool using a fine-tuned LLM to "
        "generate summaries of regulatory filings and compliance reports for "
        "analyst review. No customer-facing outputs; all summaries reviewed by "
        "compliance staff before use."
    ),
}

# Labels for the dropdown
DEMO_LABELS = list(DEMO_CASES.keys())
