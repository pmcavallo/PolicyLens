"""PolicyLens Streamlit UI — AI Risk Assessment Engine.

Professional risk management interface with tabbed assessment views,
gap analysis visualization, and executive report export.

Run: py -m streamlit run src/ui/app.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from src.assessment.engine import run_assessment
from src.assessment.schemas import (
    GapSeverity,
    RiskAssessment,
    RMFFunctionAssessment,
)
from src.output.report import generate_report
from src.ui.demo_cases import DEMO_CASES, DEMO_LABELS


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PolicyLens \u2014 AI Risk Assessment",
    page_icon="\U0001f6e1\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .tier-critical { color: #fff; background: #dc3545; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
    .tier-high { color: #fff; background: #fd7e14; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
    .tier-medium { color: #000; background: #ffc107; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
    .tier-low { color: #fff; background: #28a745; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
    .gap-critical { color: #dc3545; font-weight: bold; }
    .gap-high { color: #fd7e14; font-weight: bold; }
    .gap-medium { color: #ffc107; font-weight: bold; }
    .gap-low { color: #28a745; font-weight: bold; }
    .stMetric { border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://img.icons8.com/fluency/48/shield.png", width=40)
    st.title("PolicyLens")
    st.caption("AI Risk Assessment Engine")

    st.divider()
    st.markdown("**Regulatory Frameworks:**")
    st.markdown("- NIST AI 100-1 (AI RMF)")
    st.markdown("- NIST AI 600-1 (GenAI Profile)")
    st.markdown("- FHFA AB 2022-02")
    st.markdown("- SR 11-7")

    st.divider()
    st.markdown("**Internal Policies:**")
    st.markdown("- Meridian AI Governance Policy")
    st.markdown("- Meridian MRM Policy")

    st.divider()
    st.caption(
        "All data is synthetic. Meridian Financial Group "
        "is a fictional entity."
    )


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("\U0001f6e1\ufe0f PolicyLens")
st.markdown("**Three-layer AI risk assessment**: external regulation \u2192 internal policy \u2192 gap analysis")

# Input section
col_select, col_custom = st.columns([1, 2])

with col_select:
    selected_demo = st.selectbox(
        "Select a demo use case",
        options=["(Custom)"] + DEMO_LABELS,
        index=0,
    )

with col_custom:
    default_text = DEMO_CASES.get(selected_demo, "") if selected_demo != "(Custom)" else ""
    use_case_input = st.text_area(
        "Use case description",
        value=default_text,
        height=100,
        placeholder="Describe the AI use case to assess...",
    )

run_button = st.button("\U0001f680 Run Assessment", type="primary", use_container_width=True)


# ---------------------------------------------------------------------------
# Assessment execution
# ---------------------------------------------------------------------------

if run_button and use_case_input.strip():
    with st.spinner("Running assessment pipeline... (this takes 30-60 seconds)"):
        try:
            assessment = run_assessment(use_case_input.strip())
            st.session_state["assessment"] = assessment
            st.session_state["use_case"] = use_case_input.strip()
        except Exception as e:
            st.error(f"Assessment failed: {e}")
            st.stop()

elif run_button:
    st.warning("Please enter a use case description.")


# ---------------------------------------------------------------------------
# Display results
# ---------------------------------------------------------------------------

if "assessment" in st.session_state:
    assessment: RiskAssessment = st.session_state["assessment"]

    st.divider()

    # Tabs
    tabs = st.tabs([
        "\U0001f4cb Executive Summary",
        "\U0001f3db\ufe0f Govern",
        "\U0001f5fa\ufe0f Map",
        "\U0001f4cf Measure",
        "\u2699\ufe0f Manage",
        "\U0001f50d Gap Analysis",
        "\U0001f4dc SR 11-7",
        "\U0001f4d1 Citations",
    ])

    # -----------------------------------------------------------------------
    # Tab 1: Executive Summary
    # -----------------------------------------------------------------------
    with tabs[0]:
        _render_executive_summary(assessment)

    # -----------------------------------------------------------------------
    # Tabs 2-5: RMF Functions
    # -----------------------------------------------------------------------
    rmf_icons = ["\U0001f3db\ufe0f", "\U0001f5fa\ufe0f", "\U0001f4cf", "\u2699\ufe0f"]
    for i, func_assessment in enumerate(assessment.rmf_assessment):
        with tabs[i + 1]:
            _render_rmf_function(func_assessment)

    # -----------------------------------------------------------------------
    # Tab 6: Gap Analysis
    # -----------------------------------------------------------------------
    with tabs[5]:
        _render_gap_analysis(assessment)

    # -----------------------------------------------------------------------
    # Tab 7: SR 11-7 Alignment
    # -----------------------------------------------------------------------
    with tabs[6]:
        _render_sr_117(assessment)

    # -----------------------------------------------------------------------
    # Tab 8: Citations
    # -----------------------------------------------------------------------
    with tabs[7]:
        _render_citations(assessment)

    # -----------------------------------------------------------------------
    # Export buttons
    # -----------------------------------------------------------------------
    st.divider()
    col_export1, col_export2 = st.columns(2)

    with col_export1:
        report_md = generate_report(assessment)
        st.download_button(
            "\U0001f4e5 Export Executive Report (.md)",
            data=report_md,
            file_name=f"risk_assessment_{date.today().isoformat()}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_export2:
        assessment_json = json.dumps(assessment.model_dump(), indent=2, ensure_ascii=False)
        st.download_button(
            "\U0001f4e5 Export Raw JSON",
            data=assessment_json,
            file_name=f"risk_assessment_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Render functions
# ---------------------------------------------------------------------------

def _tier_badge(tier: str) -> str:
    """Return HTML for a colored tier badge."""
    css_class = f"tier-{tier.lower()}"
    return f'<span class="{css_class}">{tier}</span>'


def _severity_color(severity: str) -> str:
    """Return a color for gap severity."""
    return {
        "CRITICAL": "#dc3545",
        "HIGH": "#fd7e14",
        "MEDIUM": "#ffc107",
        "LOW": "#28a745",
    }.get(severity, "#6c757d")


def _render_executive_summary(assessment: RiskAssessment) -> None:
    """Render the executive summary tab."""
    # Risk tier badge
    st.markdown(
        f"### Risk Tier: {_tier_badge(assessment.risk_tier.value)}",
        unsafe_allow_html=True,
    )
    st.markdown(f"*{assessment.risk_tier_rationale}*")

    st.markdown("---")

    # Coverage metrics
    st.subheader("Coverage by RMF Function")
    cols = st.columns(4)
    for i, func in enumerate(assessment.rmf_assessment):
        with cols[i]:
            delta_color = "normal" if func.coverage_score >= 60 else "inverse"
            st.metric(
                label=func.function_name.value,
                value=f"{func.coverage_score:.0f}%",
                delta=f"{len(func.gaps)} gaps",
                delta_color=delta_color,
            )

    # Overall stats
    avg_coverage = sum(f.coverage_score for f in assessment.rmf_assessment) / 4
    total_gaps = len(assessment.gap_summary)
    critical_count = sum(1 for g in assessment.gap_summary if g.gap_severity == GapSeverity.CRITICAL)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Coverage", f"{avg_coverage:.0f}%")
    col2.metric("Total Gaps", str(total_gaps))
    col3.metric("Critical Gaps", str(critical_count))

    # Top gaps preview
    st.markdown("---")
    st.subheader("Top Gaps")
    for gap in assessment.gap_summary[:5]:
        color = _severity_color(gap.gap_severity.value)
        st.markdown(
            f'<span style="color: {color}; font-weight: bold;">'
            f'[{gap.gap_severity.value}]</span> '
            f'**{gap.gap_category}** \u2014 {gap.remediation[:120]}',
            unsafe_allow_html=True,
        )

    # Key risks
    if assessment.key_risks:
        st.markdown("---")
        st.subheader("Key Risks")
        for risk in assessment.key_risks:
            st.markdown(f"- {risk}")

    # Recommended controls
    if assessment.recommended_controls:
        st.subheader("Recommended Controls")
        for ctrl in assessment.recommended_controls:
            st.markdown(f"- {ctrl}")


def _render_rmf_function(func: RMFFunctionAssessment) -> None:
    """Render a single RMF function tab."""
    st.header(f"{func.function_name.value} Function")
    st.metric("Coverage Score", f"{func.coverage_score:.0f}%")

    # Regulatory findings
    st.subheader("Regulatory Requirements")
    if func.regulatory_findings:
        for finding in func.regulatory_findings:
            with st.expander(
                f"[{finding.framework}] {finding.section_id}: {finding.section_title[:60]}"
            ):
                st.markdown(f"**Requirement:** {finding.requirement}")
                st.markdown(f"**Applicability:** {finding.applicability.value}")
                st.markdown(f"**Recommendation:** {finding.recommendation}")
                if finding.fhfa_overlay:
                    st.info(f"**FHFA Overlay:** {finding.fhfa_overlay}")
    else:
        st.info("No regulatory findings for this function.")

    st.divider()

    # Internal findings
    st.subheader("Internal Policy Coverage")
    if func.internal_findings:
        for finding in func.internal_findings:
            adequacy_icon = {"ADEQUATE": "\u2705", "PARTIAL": "\u26a0\ufe0f", "MISSING": "\u274c"}.get(
                finding.adequacy.value, ""
            )
            with st.expander(
                f"{adequacy_icon} [{finding.policy_reference}] {finding.section_id}"
            ):
                st.markdown(f"**Coverage:** {finding.current_coverage}")
                st.markdown(f"**Adequacy:** {finding.adequacy.value}")
    else:
        st.info("No internal policy findings for this function.")

    st.divider()

    # Gaps for this function
    st.subheader("Gaps Identified")
    if func.gaps:
        for gap in func.gaps:
            color = _severity_color(gap.gap_severity.value)
            with st.expander(
                f"[{gap.gap_severity.value}] {gap.gap_category}"
            ):
                st.markdown(f"**External Requirement:** {gap.external_requirement}")
                st.markdown(f"**External Citation:** {gap.external_citation}")
                st.markdown(f"**Internal Coverage:** {gap.internal_coverage}")
                st.markdown(f"**Internal Citation:** {gap.internal_citation}")
                st.markdown(
                    f'**Severity:** <span style="color: {color}; font-weight: bold;">'
                    f'{gap.gap_severity.value}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Remediation:** {gap.remediation}")
    else:
        st.success("No gaps identified for this function.")


def _render_gap_analysis(assessment: RiskAssessment) -> None:
    """Render the full gap analysis tab as a sortable table."""
    st.header("Gap Analysis")
    st.markdown(
        "Complete gap analysis across all RMF functions. "
        "Gaps represent areas where internal policy falls short of regulatory requirements."
    )

    if not assessment.gap_summary:
        st.success("No gaps identified.")
        return

    # Build dataframe
    rows = []
    for gap in assessment.gap_summary:
        rows.append({
            "Severity": gap.gap_severity.value,
            "Category": gap.gap_category,
            "External Requirement": gap.external_requirement[:80],
            "External Citation": gap.external_citation,
            "Internal Status": gap.internal_coverage[:50],
            "Internal Citation": gap.internal_citation,
            "Remediation": gap.remediation[:80],
        })

    df = pd.DataFrame(rows)

    # Color-coded severity column
    def _color_severity(val: str) -> str:
        colors = {
            "CRITICAL": "background-color: #dc3545; color: white; font-weight: bold",
            "HIGH": "background-color: #fd7e14; color: white; font-weight: bold",
            "MEDIUM": "background-color: #ffc107; color: black; font-weight: bold",
            "LOW": "background-color: #28a745; color: white; font-weight: bold",
        }
        return colors.get(val, "")

    styled = df.style.map(_color_severity, subset=["Severity"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Detailed view
    st.subheader("Detailed Gap Findings")
    for gap in assessment.gap_summary:
        color = _severity_color(gap.gap_severity.value)
        with st.expander(f"[{gap.gap_severity.value}] {gap.gap_category}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**External Requirement:**")
                st.markdown(gap.external_requirement)
                st.markdown(f"*Citation: {gap.external_citation}*")
            with col2:
                st.markdown("**Internal Coverage:**")
                st.markdown(gap.internal_coverage)
                st.markdown(f"*Citation: {gap.internal_citation}*")
            st.markdown(f"**Remediation:** {gap.remediation}")


def _render_sr_117(assessment: RiskAssessment) -> None:
    """Render SR 11-7 alignment tab."""
    st.header("SR 11-7 Alignment")
    st.markdown(
        "Findings specific to the Federal Reserve's Supervisory Guidance "
        "on Model Risk Management (SR Letter 11-7)."
    )

    if not assessment.sr_11_7_alignment:
        st.info("No SR 11-7 specific findings for this use case.")
        return

    for finding in assessment.sr_11_7_alignment:
        with st.expander(f"[{finding.section_id}] {finding.section_title[:60]}"):
            st.markdown(f"**Requirement:** {finding.requirement}")
            st.markdown(f"**Applicability:** {finding.applicability.value}")
            st.markdown(f"**Recommendation:** {finding.recommendation}")
            if finding.fhfa_overlay:
                st.info(f"**FHFA Overlay:** {finding.fhfa_overlay}")


def _render_citations(assessment: RiskAssessment) -> None:
    """Render all citations tab."""
    st.header("All Citations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("External Regulatory Citations")
        if assessment.external_citations:
            for citation in assessment.external_citations:
                st.markdown(f"- {citation}")
        else:
            st.info("No external citations.")

    with col2:
        st.subheader("Internal Policy Citations")
        if assessment.internal_citations:
            for citation in assessment.internal_citations:
                st.markdown(f"- {citation}")
        else:
            st.info("No internal citations.")
