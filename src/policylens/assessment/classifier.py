"""Risk tier classifier using Claude API.

Classifies AI use cases into risk tiers (Critical/High/Medium/Low) based on
decision impact, population affected, data sensitivity, autonomy level, and
GenAI involvement.
"""

from __future__ import annotations

from dataclasses import dataclass

import anthropic


CLASSIFIER_PROMPT = """\
You are an AI risk classification specialist at a financial services firm. \
Classify the following AI use case into a risk tier based on these factors:

RISK TIER DEFINITIONS:
- Critical: Customer-facing decisioning affecting credit, lending, or account access; \
uses protected-class data; autonomous decisions without human review; regulatory scrutiny expected.
- High: Material business impact; affects large populations; uses sensitive data; \
limited human oversight; or involves GenAI in customer-facing contexts.
- Medium: Internal analytics with moderate business impact; human review of outputs; \
limited sensitive data exposure.
- Low: Internal-only tools; no customer impact; no sensitive data; fully supervised use.

CLASSIFICATION FACTORS (evaluate each):
1. Decision Impact: What decisions does the model influence? How consequential are errors?
2. Population Affected: How many people are impacted? Are vulnerable populations involved?
3. Data Sensitivity: Does it use PII, protected-class data, financial data, alternative data?
4. Autonomy Level: Fully automated decisions, human-in-the-loop, or advisory only?
5. GenAI Involvement: Does it use generative AI? If so, hallucination/data leakage risks apply.

USE CASE:
{use_case}

Respond with EXACTLY this format (no other text):
TIER: <Critical|High|Medium|Low>
RATIONALE: <2-3 sentence rationale covering the key risk factors>
DECISION_IMPACT: <one sentence>
POPULATION_AFFECTED: <one sentence>
DATA_SENSITIVITY: <one sentence>
AUTONOMY_LEVEL: <one sentence>
GENAI_INVOLVEMENT: <one sentence>
"""


@dataclass
class ClassificationResult:
    """Result of risk tier classification."""
    risk_tier: str
    rationale: str
    decision_impact: str
    population_affected: str
    data_sensitivity: str
    autonomy_level: str
    genai_involvement: str


def _parse_classification_response(text: str) -> ClassificationResult:
    """Parse the structured classifier response into a ClassificationResult."""
    lines: dict[str, str] = {}
    for line in text.strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            lines[key.strip().upper()] = value.strip()

    tier = lines.get("TIER", "High")
    # Normalize tier value
    tier_map = {"CRITICAL": "Critical", "HIGH": "High", "MEDIUM": "Medium", "LOW": "Low"}
    tier = tier_map.get(tier.upper(), "High")

    return ClassificationResult(
        risk_tier=tier,
        rationale=lines.get("RATIONALE", ""),
        decision_impact=lines.get("DECISION_IMPACT", ""),
        population_affected=lines.get("POPULATION_AFFECTED", ""),
        data_sensitivity=lines.get("DATA_SENSITIVITY", ""),
        autonomy_level=lines.get("AUTONOMY_LEVEL", ""),
        genai_involvement=lines.get("GENAI_INVOLVEMENT", ""),
    )


def classify_risk_tier(
    use_case: str,
    api_key: str,
    model: str = "claude-sonnet-4-5-20250929",
) -> ClassificationResult:
    """Classify a use case into a risk tier using Claude API.

    Args:
        use_case: Description of the AI use case.
        api_key: Anthropic API key.
        model: Claude model to use.

    Returns:
        ClassificationResult with tier, rationale, and factor assessments.
    """
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[
            {"role": "user", "content": CLASSIFIER_PROMPT.format(use_case=use_case)}
        ],
    )
    return _parse_classification_response(response.content[0].text)
