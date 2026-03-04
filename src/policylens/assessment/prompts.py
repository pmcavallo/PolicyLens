"""Assessment prompt templates for the three-layer risk assessment.

The core prompt instructs the LLM to:
1. Organize findings by NIST RMF function (Govern, Map, Measure, Manage)
2. For each function: cite specific external requirements AND internal coverage
3. Identify gaps where internal policy falls short of external requirements
4. Output valid JSON matching the Pydantic schemas
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are an AI Risk Assessment Specialist at a financial services institution. \
You produce structured risk assessments that would be presented to a Risk Committee.

Your assessments are grounded ONLY in the regulatory framework excerpts and \
internal policy excerpts provided. Never fabricate citations. If a section is \
referenced, it must appear in the provided context.

IMPORTANT: Meridian Financial Group is a fictional company used for demonstration. \
All data is synthetic.

OUTPUT FORMAT: You must respond with valid JSON matching the schema provided. \
No markdown, no commentary — only the JSON object."""


def build_assessment_prompt(
    use_case: str,
    risk_tier: str,
    risk_tier_rationale: str,
    external_chunks: list[dict],
    internal_chunks: list[dict],
) -> str:
    """Build the full assessment prompt with retrieved context.

    Args:
        use_case: Description of the AI use case.
        risk_tier: Classified risk tier (Critical/High/Medium/Low).
        risk_tier_rationale: Explanation of the tier classification.
        external_chunks: List of dicts with 'text' and 'metadata' from regulatory collection.
        internal_chunks: List of dicts with 'text' and 'metadata' from internal collection.

    Returns:
        Formatted prompt string for the LLM.
    """
    external_context = _format_chunks(external_chunks, "REGULATORY FRAMEWORK")
    internal_context = _format_chunks(internal_chunks, "INTERNAL POLICY")

    return f"""\
Produce a comprehensive AI risk assessment for the following use case.

═══════════════════════════════════════════════════════════════════════
USE CASE
═══════════════════════════════════════════════════════════════════════
{use_case}

RISK TIER: {risk_tier}
RATIONALE: {risk_tier_rationale}

═══════════════════════════════════════════════════════════════════════
REGULATORY FRAMEWORK EXCERPTS (External Requirements)
These are the relevant sections from NIST AI 100-1, NIST AI 600-1,
FHFA AB 2022-02, and SR 11-7. Use these as the basis for regulatory
findings and citations.
═══════════════════════════════════════════════════════════════════════
{external_context}

═══════════════════════════════════════════════════════════════════════
INTERNAL POLICY EXCERPTS (Meridian Financial Group)
These are the relevant sections from Meridian's AI Governance Policy
and Model Risk Management Policy. Use these to assess internal
coverage and identify gaps.
═══════════════════════════════════════════════════════════════════════
{internal_context}

═══════════════════════════════════════════════════════════════════════
ASSESSMENT INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════

Produce a JSON object with this exact structure:

{{
  "use_case_summary": "<2-3 sentence summary of the use case>",
  "risk_tier": "{risk_tier}",
  "risk_tier_rationale": "<rationale>",
  "rmf_assessment": [
    {{
      "function_name": "Govern",
      "regulatory_findings": [
        {{
          "requirement": "<what the regulation requires>",
          "framework": "<e.g. NIST AI 100-1>",
          "section_id": "<e.g. GOVERN 1.1>",
          "section_title": "<section title>",
          "applicability": "<HIGH|MEDIUM|LOW>",
          "recommendation": "<specific action to take>",
          "fhfa_overlay": "<additional FHFA requirement, or null>"
        }}
      ],
      "internal_findings": [
        {{
          "policy_reference": "<e.g. Meridian AI Governance Policy>",
          "section_id": "<e.g. Section 2: Governance Structure and Roles>",
          "current_coverage": "<what the policy currently says>",
          "adequacy": "<ADEQUATE|PARTIAL|MISSING>"
        }}
      ],
      "gaps": [
        {{
          "gap_category": "<e.g. GenAI Governance>",
          "external_requirement": "<what regulation requires>",
          "external_citation": "<e.g. NIST AI 100-1, GOVERN 1.1>",
          "internal_coverage": "<what internal policy says, or NOT ADDRESSED>",
          "internal_citation": "<e.g. AI Governance Policy, Section 2 or N/A>",
          "gap_severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
          "remediation": "<specific recommended action>"
        }}
      ],
      "coverage_score": <0-100 float>
    }},
    ... repeat for "Map", "Measure", "Manage" (exactly 4 items)
  ],
  "sr_11_7_alignment": [
    <RegulatoryFinding objects specific to SR 11-7>
  ],
  "gap_summary": [
    <Top 5-8 most important GapFinding objects across all functions, sorted by severity>
  ],
  "key_risks": ["<risk 1>", "<risk 2>", ...],
  "recommended_controls": ["<control 1>", "<control 2>", ...],
  "external_citations": ["<framework, section_id>", ...],
  "internal_citations": ["<policy, section_id>", ...]
}}

CRITICAL RULES:
1. You MUST produce exactly 4 items in rmf_assessment: Govern, Map, Measure, Manage (in order).
2. Every regulatory_finding MUST cite a section_id that appears in the REGULATORY FRAMEWORK EXCERPTS above.
3. Every internal_finding MUST cite a section_id from the INTERNAL POLICY EXCERPTS above.
4. For gaps: if internal policy does NOT address a regulatory requirement, set internal_coverage to "NOT ADDRESSED" and internal_citation to "N/A".
5. gap_severity should reflect the risk to the institution:
   - CRITICAL: Regulatory requirement completely unaddressed, high compliance risk
   - HIGH: Significant gap with material risk
   - MEDIUM: Partial coverage that needs enhancement
   - LOW: Minor gap, easily remediated
6. coverage_score: 100 = internal policy fully covers all regulatory requirements for this function; 0 = no coverage at all. Be realistic — most firms have partial coverage.
7. sr_11_7_alignment: include 2-4 findings specifically from SR 11-7 that apply to this use case.
8. gap_summary: the top 5-8 most significant gaps across ALL functions, sorted by severity (CRITICAL first).
9. external_citations and internal_citations: flat lists of ALL unique citations used anywhere in the assessment.
10. Use the exact enum values: "Critical"/"High"/"Medium"/"Low" for risk_tier; "HIGH"/"MEDIUM"/"LOW" for applicability; "ADEQUATE"/"PARTIAL"/"MISSING" for adequacy; "CRITICAL"/"HIGH"/"MEDIUM"/"LOW" for gap_severity; "Govern"/"Map"/"Measure"/"Manage" for function_name.

Respond with ONLY the JSON object. No markdown fences, no explanation."""


def _format_chunks(chunks: list[dict], label: str) -> str:
    """Format retrieved chunks into a readable context block."""
    if not chunks:
        return f"[No {label} excerpts retrieved]"

    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        framework = meta.get("framework_name", "Unknown")
        section_id = meta.get("section_id", "Unknown")
        section_title = meta.get("section_title", "")
        rmf_func = meta.get("rmf_function", "")
        doc_type = meta.get("document_type", "")

        header_parts = [f"[{i}] {framework}"]
        if rmf_func:
            header_parts.append(f"Function: {rmf_func}")
        header_parts.append(f"Section: {section_id}")
        if section_title:
            header_parts.append(f"Title: {section_title}")

        header = " | ".join(header_parts)
        text = chunk.get("text", "")

        parts.append(f"{header}\n{text}")

    return "\n\n---\n\n".join(parts)
