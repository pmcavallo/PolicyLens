"""Assessment engine — the orchestrator that wires everything together.

Pipeline:
1. Accept use case description
2. Classify risk tier
3. Query both ChromaDB collections
4. Build assessment prompt with retrieved chunks
5. Call Claude API for structured assessment
6. Validate output against Pydantic schemas
7. Run gap analysis post-processing
8. Return validated RiskAssessment object
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from src.assessment.classifier import classify_risk_tier, ClassificationResult
from src.assessment.gap_analyzer import enhance_assessment
from src.assessment.prompts import SYSTEM_PROMPT, build_assessment_prompt
from src.assessment.schemas import RiskAssessment
from src.ingestion.vectorstore import get_client, query_both_collections, DEFAULT_PERSIST_DIR


def _get_api_key() -> str:
    """Load Anthropic API key from .env or environment."""
    load_dotenv(override=True)
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key or key == "your-api-key-here":
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Update .env with your API key."
        )
    return key


def _retrieval_results_to_chunk_dicts(results: dict) -> list[dict]:
    """Convert ChromaDB query results into the chunk dict format expected by prompts."""
    chunks: list[dict] = []
    if not results.get("documents") or not results["documents"][0]:
        return chunks

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for doc, meta in zip(documents, metadatas):
        chunks.append({"text": doc, "metadata": meta})

    return chunks


def run_assessment(
    use_case: str,
    persist_dir: Path = DEFAULT_PERSIST_DIR,
    model: str = "claude-sonnet-4-5-20250929",
    n_results: int = 15,
) -> RiskAssessment:
    """Run the full assessment pipeline.

    Args:
        use_case: Description of the AI use case to assess.
        persist_dir: ChromaDB persistence directory.
        model: Claude model for the assessment (not the classifier).
        n_results: Number of chunks to retrieve per collection.

    Returns:
        Validated RiskAssessment object with gap analysis.
    """
    api_key = _get_api_key()

    # Step 1: Classify risk tier
    print("[1/5] Classifying risk tier...")
    classification = classify_risk_tier(use_case, api_key)
    print(f"  Tier: {classification.risk_tier}")
    print(f"  Rationale: {classification.rationale}")

    # Step 2: Retrieve from both collections
    print("[2/5] Retrieving regulatory and internal policy context...")
    client = get_client(persist_dir)
    results = query_both_collections(client, use_case, n_results=n_results)

    external_chunks = _retrieval_results_to_chunk_dicts(results["external"])
    internal_chunks = _retrieval_results_to_chunk_dicts(results["internal"])
    print(f"  Retrieved {len(external_chunks)} external, {len(internal_chunks)} internal chunks")

    # Step 3: Build prompt
    print("[3/5] Building assessment prompt...")
    prompt = build_assessment_prompt(
        use_case=use_case,
        risk_tier=classification.risk_tier,
        risk_tier_rationale=classification.rationale,
        external_chunks=external_chunks,
        internal_chunks=internal_chunks,
    )

    # Step 4: Call Claude API
    print("[4/5] Generating structured assessment...")
    client_api = anthropic.Anthropic(api_key=api_key)
    response = client_api.messages.create(
        model=model,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_json = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw_json.startswith("```"):
        raw_json = raw_json.split("\n", 1)[1]
    if raw_json.endswith("```"):
        raw_json = raw_json.rsplit("```", 1)[0]
    raw_json = raw_json.strip()

    # Step 5: Validate and enhance
    print("[5/5] Validating and enhancing assessment...")
    try:
        assessment_data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"  ERROR: Invalid JSON from LLM: {e}")
        print(f"  First 500 chars: {raw_json[:500]}")
        raise

    try:
        assessment = RiskAssessment.model_validate(assessment_data)
    except Exception as e:
        print(f"  ERROR: Schema validation failed: {e}")
        # Attempt lenient parsing with partial data
        raise

    # Post-processing: gap analysis enhancement
    assessment = enhance_assessment(assessment)

    _print_summary(assessment)
    return assessment


def _print_summary(assessment: RiskAssessment) -> None:
    """Print a concise summary of the assessment results."""
    print("\n" + "=" * 60)
    print("ASSESSMENT COMPLETE")
    print("=" * 60)
    print(f"  Use Case: {assessment.use_case_summary[:80]}...")
    print(f"  Risk Tier: {assessment.risk_tier.value}")

    for func in assessment.rmf_assessment:
        n_reg = len(func.regulatory_findings)
        n_int = len(func.internal_findings)
        n_gaps = len(func.gaps)
        print(f"  {func.function_name.value}: {n_reg} regulatory, {n_int} internal, {n_gaps} gaps, coverage={func.coverage_score}%")

    total_gaps = len(assessment.gap_summary)
    critical_gaps = sum(1 for g in assessment.gap_summary if g.gap_severity == "CRITICAL")
    high_gaps = sum(1 for g in assessment.gap_summary if g.gap_severity == "HIGH")
    print(f"\n  Gap Summary: {total_gaps} gaps ({critical_gaps} critical, {high_gaps} high)")
    print(f"  External Citations: {len(assessment.external_citations)}")
    print(f"  Internal Citations: {len(assessment.internal_citations)}")
