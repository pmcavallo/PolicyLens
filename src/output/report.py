"""Executive report generator in Risk Committee format.

Converts a RiskAssessment object into a markdown report matching
the format specified in PROJECT_PLAN.md. Designed to look like an
internal risk management artifact, not a developer JSON dump.
"""

from __future__ import annotations

from datetime import date

from src.assessment.schemas import (
    GapFinding,
    GapSeverity,
    RiskAssessment,
    RMFFunctionAssessment,
)


def generate_report(assessment: RiskAssessment) -> str:
    """Generate a complete executive report as markdown.

    Args:
        assessment: Validated RiskAssessment object.

    Returns:
        Formatted markdown string ready for export.
    """
    today = date.today().strftime("%B %d, %Y")
    avg_coverage = _avg_coverage(assessment)

    sections = [
        _header(assessment, today),
        _executive_summary(assessment, avg_coverage),
        _risk_tier_determination(assessment),
        _regulatory_requirements(assessment),
        _internal_policy_alignment(assessment),
        _gap_analysis(assessment),
        _remediation_priorities(assessment),
        _sr_11_7_alignment(assessment),
        _appendix_citations(assessment),
        _disclaimer(),
    ]

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def _header(assessment: RiskAssessment, today: str) -> str:
    return f"""---

# MERIDIAN FINANCIAL GROUP
## AI Risk Assessment Report

**Use Case:** {assessment.use_case_summary}

**Assessment Date:** {today}

**Prepared by:** AI Risk Management, Second Line of Defense

**Risk Tier:** {assessment.risk_tier.value}

---"""


def _executive_summary(assessment: RiskAssessment, avg_coverage: float) -> str:
    total_gaps = len(assessment.gap_summary)
    critical = sum(1 for g in assessment.gap_summary if g.gap_severity == GapSeverity.CRITICAL)
    high = sum(1 for g in assessment.gap_summary if g.gap_severity == GapSeverity.HIGH)

    top_rec = assessment.recommended_controls[0] if assessment.recommended_controls else "See remediation priorities below."

    lines = [
        "## 1. Executive Summary",
        "",
        assessment.use_case_summary,
        "",
        f"**Risk Tier:** {assessment.risk_tier.value} \u2014 {assessment.risk_tier_rationale}",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total gaps identified | {total_gaps} |",
        f"| Critical gaps | {critical} |",
        f"| High gaps | {high} |",
        f"| Overall coverage score | {avg_coverage:.0f}% |",
        f"| External citations | {len(assessment.external_citations)} |",
        f"| Internal citations | {len(assessment.internal_citations)} |",
        "",
        f"**Top Recommendation:** {top_rec}",
    ]
    return "\n".join(lines)


def _risk_tier_determination(assessment: RiskAssessment) -> str:
    lines = [
        "## 2. Risk Tier Determination",
        "",
        f"**Tier:** {assessment.risk_tier.value}",
        "",
        f"{assessment.risk_tier_rationale}",
        "",
        "**Key Risks:**",
    ]
    for risk in assessment.key_risks:
        lines.append(f"- {risk}")

    return "\n".join(lines)


def _regulatory_requirements(assessment: RiskAssessment) -> str:
    lines = [
        "## 3. Regulatory Requirements by RMF Function",
    ]

    for i, func in enumerate(assessment.rmf_assessment, 1):
        lines.append(f"\n### 3.{i} {func.function_name.value}")
        lines.append(f"\n**Coverage Score:** {func.coverage_score:.0f}%\n")

        if func.regulatory_findings:
            for finding in func.regulatory_findings:
                fhfa = f" | *FHFA: {finding.fhfa_overlay}*" if finding.fhfa_overlay else ""
                lines.append(
                    f"- **{finding.requirement}** "
                    f"({finding.framework}, {finding.section_id})"
                    f" \u2014 Applicability: {finding.applicability.value}{fhfa}"
                )
                lines.append(f"  - *Recommendation:* {finding.recommendation}")
        else:
            lines.append("*No specific findings for this function.*")

    return "\n".join(lines)


def _internal_policy_alignment(assessment: RiskAssessment) -> str:
    lines = [
        "## 4. Internal Policy Alignment",
    ]

    for func in assessment.rmf_assessment:
        lines.append(f"\n### {func.function_name.value}\n")

        if func.internal_findings:
            lines.append("| Policy | Section | Coverage | Adequacy |")
            lines.append("|--------|---------|----------|----------|")
            for finding in func.internal_findings:
                adequacy_icon = {
                    "ADEQUATE": "\u2705",
                    "PARTIAL": "\u26a0\ufe0f",
                    "MISSING": "\u274c",
                }.get(finding.adequacy.value, "")
                coverage_short = finding.current_coverage[:80]
                if len(finding.current_coverage) > 80:
                    coverage_short += "..."
                lines.append(
                    f"| {finding.policy_reference} | {finding.section_id} "
                    f"| {coverage_short} | {adequacy_icon} {finding.adequacy.value} |"
                )
        else:
            lines.append("*No internal policy findings for this function.*")

    return "\n".join(lines)


def _gap_analysis(assessment: RiskAssessment) -> str:
    lines = [
        "## 5. Gap Analysis",
        "",
        "Gaps sorted by severity. CRITICAL gaps represent areas where regulatory "
        "requirements are completely unaddressed by internal policy.",
        "",
        "| Severity | Gap Category | External Requirement | Internal Status | Remediation |",
        "|----------|-------------|---------------------|-----------------|-------------|",
    ]

    for gap in assessment.gap_summary:
        severity_icon = {
            "CRITICAL": "\U0001f534",
            "HIGH": "\U0001f7e0",
            "MEDIUM": "\U0001f7e1",
            "LOW": "\U0001f7e2",
        }.get(gap.gap_severity.value, "")

        ext_short = gap.external_requirement[:60]
        if len(gap.external_requirement) > 60:
            ext_short += "..."
        int_short = gap.internal_coverage[:40]
        if len(gap.internal_coverage) > 40:
            int_short += "..."
        rem_short = gap.remediation[:60]
        if len(gap.remediation) > 60:
            rem_short += "..."

        lines.append(
            f"| {severity_icon} **{gap.gap_severity.value}** "
            f"| {gap.gap_category} | {ext_short} "
            f"| {int_short} | {rem_short} |"
        )

    return "\n".join(lines)


def _remediation_priorities(assessment: RiskAssessment) -> str:
    lines = [
        "## 6. Remediation Priorities",
        "",
    ]

    # Use gap_summary sorted by severity as priorities
    critical_gaps = [g for g in assessment.gap_summary if g.gap_severity == GapSeverity.CRITICAL]
    high_gaps = [g for g in assessment.gap_summary if g.gap_severity == GapSeverity.HIGH]
    other_gaps = [g for g in assessment.gap_summary if g.gap_severity not in (GapSeverity.CRITICAL, GapSeverity.HIGH)]

    priority = 1
    for gap in critical_gaps:
        lines.append(
            f"**Priority {priority} (CRITICAL):** {gap.gap_category} \u2014 "
            f"{gap.remediation} *(Ref: {gap.external_citation})*"
        )
        lines.append("")
        priority += 1

    for gap in high_gaps:
        lines.append(
            f"**Priority {priority} (HIGH):** {gap.gap_category} \u2014 "
            f"{gap.remediation} *(Ref: {gap.external_citation})*"
        )
        lines.append("")
        priority += 1

    for gap in other_gaps:
        lines.append(
            f"**Priority {priority} ({gap.gap_severity.value}):** {gap.gap_category} \u2014 "
            f"{gap.remediation}"
        )
        lines.append("")
        priority += 1

    return "\n".join(lines)


def _sr_11_7_alignment(assessment: RiskAssessment) -> str:
    lines = [
        "## 7. SR 11-7 Alignment",
        "",
    ]

    if assessment.sr_11_7_alignment:
        for finding in assessment.sr_11_7_alignment:
            lines.append(
                f"- **{finding.section_id}: {finding.section_title}** \u2014 "
                f"{finding.requirement}"
            )
            lines.append(f"  - *Recommendation:* {finding.recommendation}")
            lines.append("")
    else:
        lines.append("*No SR 11-7 specific findings for this use case.*")

    return "\n".join(lines)


def _appendix_citations(assessment: RiskAssessment) -> str:
    lines = [
        "## 8. Appendix: Regulatory Citations",
        "",
        "### External Regulatory Citations",
        "",
    ]
    for citation in assessment.external_citations:
        lines.append(f"- {citation}")

    lines.append("")
    lines.append("### Internal Policy Citations")
    lines.append("")
    for citation in assessment.internal_citations:
        lines.append(f"- {citation}")

    return "\n".join(lines)


def _disclaimer() -> str:
    return (
        "---\n\n"
        "*This assessment was generated by PolicyLens, an AI-powered risk assessment tool. "
        "All internal policy references are to Meridian Financial Group, a fictional entity. "
        "All data is synthetic. This report is for demonstration purposes only and does not "
        "constitute legal, regulatory, or compliance advice.*"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _avg_coverage(assessment: RiskAssessment) -> float:
    """Calculate average coverage score across all RMF functions."""
    scores = [f.coverage_score for f in assessment.rmf_assessment]
    return sum(scores) / len(scores) if scores else 0.0
