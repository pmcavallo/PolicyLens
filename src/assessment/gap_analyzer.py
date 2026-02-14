"""Post-processing gap analysis logic.

Enhances the LLM's gap findings by:
- Ensuring every MISSING internal coverage is flagged
- Sorting gaps by severity
- Calculating coverage_score per RMF function
- Generating a consolidated gap_summary
"""

from __future__ import annotations

from src.assessment.schemas import (
    GapFinding,
    GapSeverity,
    RiskAssessment,
    RMFFunctionAssessment,
    Adequacy,
)


# Severity ordering for sorting
_SEVERITY_ORDER = {
    GapSeverity.CRITICAL: 0,
    GapSeverity.HIGH: 1,
    GapSeverity.MEDIUM: 2,
    GapSeverity.LOW: 3,
}


def recalculate_coverage_scores(assessment: RiskAssessment) -> RiskAssessment:
    """Recalculate coverage_score for each RMF function based on internal findings.

    Score formula:
    - Each internal finding with ADEQUATE = 100% weight
    - Each internal finding with PARTIAL = 50% weight
    - Each internal finding with MISSING = 0% weight
    - Score = weighted sum / total regulatory findings * 100

    If there are gaps with no corresponding internal findings, those count as MISSING.
    """
    for func_assessment in assessment.rmf_assessment:
        total_items = len(func_assessment.regulatory_findings)
        if total_items == 0:
            func_assessment.coverage_score = 0.0
            continue

        # Count adequacy from internal findings
        adequate_count = sum(
            1 for f in func_assessment.internal_findings
            if f.adequacy == Adequacy.ADEQUATE
        )
        partial_count = sum(
            1 for f in func_assessment.internal_findings
            if f.adequacy == Adequacy.PARTIAL
        )

        # Gaps with severity CRITICAL or HIGH that have "NOT ADDRESSED" coverage
        # indicate areas not covered by internal findings at all
        unaddressed_gaps = sum(
            1 for g in func_assessment.gaps
            if g.internal_coverage.upper() == "NOT ADDRESSED"
        )

        # Score: ADEQUATE items get full credit, PARTIAL get half
        # The denominator is the larger of regulatory findings count or
        # (internal findings + unaddressed gaps) to avoid inflated scores
        denominator = max(total_items, adequate_count + partial_count + unaddressed_gaps)
        if denominator == 0:
            func_assessment.coverage_score = 0.0
        else:
            score = ((adequate_count * 1.0) + (partial_count * 0.5)) / denominator * 100
            func_assessment.coverage_score = round(min(score, 100.0), 1)

    return assessment


def sort_gaps_by_severity(gaps: list[GapFinding]) -> list[GapFinding]:
    """Sort gap findings by severity (CRITICAL first)."""
    return sorted(gaps, key=lambda g: _SEVERITY_ORDER.get(g.gap_severity, 99))


def build_gap_summary(assessment: RiskAssessment, max_gaps: int = 8) -> list[GapFinding]:
    """Consolidate the most significant gaps across all RMF functions.

    Collects all gaps from individual function assessments, deduplicates by
    gap_category, and returns the top N sorted by severity.
    """
    all_gaps: list[GapFinding] = []
    seen_categories: set[str] = set()

    # Collect from function assessments
    for func_assessment in assessment.rmf_assessment:
        for gap in func_assessment.gaps:
            if gap.gap_category not in seen_categories:
                all_gaps.append(gap)
                seen_categories.add(gap.gap_category)

    # Also include any existing gap_summary entries not already captured
    for gap in assessment.gap_summary:
        if gap.gap_category not in seen_categories:
            all_gaps.append(gap)
            seen_categories.add(gap.gap_category)

    # Sort and truncate
    sorted_gaps = sort_gaps_by_severity(all_gaps)
    return sorted_gaps[:max_gaps]


def collect_citations(assessment: RiskAssessment) -> tuple[list[str], list[str]]:
    """Collect all unique external and internal citations from the assessment."""
    external: set[str] = set()
    internal: set[str] = set()

    for func_assessment in assessment.rmf_assessment:
        for finding in func_assessment.regulatory_findings:
            external.add(f"{finding.framework}, {finding.section_id}")

        for finding in func_assessment.internal_findings:
            internal.add(f"{finding.policy_reference}, {finding.section_id}")

        for gap in func_assessment.gaps:
            if gap.external_citation and gap.external_citation != "N/A":
                external.add(gap.external_citation)
            if gap.internal_citation and gap.internal_citation != "N/A":
                internal.add(gap.internal_citation)

    for finding in assessment.sr_11_7_alignment:
        external.add(f"{finding.framework}, {finding.section_id}")

    return sorted(external), sorted(internal)


def enhance_assessment(assessment: RiskAssessment) -> RiskAssessment:
    """Run all post-processing enhancements on an assessment.

    This is the main entry point for gap analysis post-processing:
    1. Recalculate coverage scores
    2. Sort gaps within each function
    3. Build consolidated gap summary
    4. Collect and deduplicate all citations
    """
    # 1. Recalculate coverage scores
    assessment = recalculate_coverage_scores(assessment)

    # 2. Sort gaps within each function assessment
    for func_assessment in assessment.rmf_assessment:
        func_assessment.gaps = sort_gaps_by_severity(func_assessment.gaps)

    # 3. Build consolidated gap summary
    assessment.gap_summary = build_gap_summary(assessment)

    # 4. Collect citations
    ext_citations, int_citations = collect_citations(assessment)
    assessment.external_citations = ext_citations
    assessment.internal_citations = int_citations

    return assessment
