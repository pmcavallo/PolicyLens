"""Pydantic schemas for structured risk assessment output.

These schemas enforce that every finding has citations, all four RMF functions
are covered, and gap analysis is clearly structured. Designed to produce
Risk Committee-ready output, not developer JSON dumps.

Schema hierarchy from PROJECT_PLAN.md:
  RiskAssessment
    -> RMFFunctionAssessment (one per function: Govern, Map, Measure, Manage)
        -> RegulatoryFinding (what regulation requires)
        -> InternalPolicyFinding (what internal policy covers)
        -> GapFinding (where internal falls short of external)
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Applicability(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Adequacy(str, Enum):
    ADEQUATE = "ADEQUATE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


class GapSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RMFFunction(str, Enum):
    GOVERN = "Govern"
    MAP = "Map"
    MEASURE = "Measure"
    MANAGE = "Manage"


class RegulatoryFinding(BaseModel):
    """A specific requirement from an external regulatory framework."""
    requirement: str = Field(description="What the framework requires")
    framework: str = Field(description="Source framework, e.g. 'NIST AI 100-1'")
    section_id: str = Field(description="Section reference, e.g. 'GOVERN 1.1'")
    section_title: str = Field(description="Section title for readability")
    applicability: Applicability = Field(description="Relevance to this use case")
    recommendation: str = Field(description="Specific control or action to implement")
    fhfa_overlay: Optional[str] = Field(
        default=None,
        description="Additional FHFA requirement if applicable",
    )


class InternalPolicyFinding(BaseModel):
    """Assessment of internal policy coverage for a specific area."""
    policy_reference: str = Field(
        description="Internal policy name, e.g. 'Meridian AI Governance Policy'",
    )
    section_id: str = Field(
        description="Internal section reference, e.g. 'Section 6: Ongoing Monitoring'",
    )
    current_coverage: str = Field(description="What the internal policy currently says")
    adequacy: Adequacy = Field(description="Coverage assessment")


class GapFinding(BaseModel):
    """A gap between external regulatory requirements and internal policy."""
    gap_category: str = Field(
        description="Category, e.g. 'GenAI Governance', 'Monitoring Frequency'",
    )
    external_requirement: str = Field(description="What regulation requires")
    external_citation: str = Field(
        description="Regulatory citation, e.g. 'NIST AI 100-1, MEASURE 2.6'",
    )
    internal_coverage: str = Field(
        description="What internal policy says, or 'NOT ADDRESSED'",
    )
    internal_citation: str = Field(
        description="Internal citation, e.g. 'AI Governance Policy, Section 6' or 'N/A'",
    )
    gap_severity: GapSeverity = Field(description="Severity of the gap")
    remediation: str = Field(description="Specific recommended action")


class RMFFunctionAssessment(BaseModel):
    """Assessment organized by one NIST AI RMF function."""
    function_name: RMFFunction
    regulatory_findings: list[RegulatoryFinding] = Field(default_factory=list)
    internal_findings: list[InternalPolicyFinding] = Field(default_factory=list)
    gaps: list[GapFinding] = Field(default_factory=list)
    coverage_score: float = Field(
        ge=0, le=100,
        description="0-100, how well internal policy covers this function",
    )


class RiskAssessment(BaseModel):
    """Complete risk assessment for an AI use case.

    This is the top-level output schema. Every assessment must include:
    - Risk tier with rationale
    - Findings organized by all four RMF functions
    - SR 11-7 specific alignment
    - Gap analysis summary
    - Full citation lists for auditability
    """
    use_case_summary: str
    risk_tier: RiskTier
    risk_tier_rationale: str
    rmf_assessment: list[RMFFunctionAssessment] = Field(
        min_length=4, max_length=4,
        description="One assessment per RMF function (Govern, Map, Measure, Manage)",
    )
    sr_11_7_alignment: list[RegulatoryFinding] = Field(
        default_factory=list,
        description="SR 11-7 specific findings",
    )
    gap_summary: list[GapFinding] = Field(
        default_factory=list,
        description="Top-level gap analysis across all functions",
    )
    key_risks: list[str] = Field(default_factory=list)
    recommended_controls: list[str] = Field(default_factory=list)
    external_citations: list[str] = Field(
        default_factory=list,
        description="All cited regulatory sections",
    )
    internal_citations: list[str] = Field(
        default_factory=list,
        description="All cited internal policy sections",
    )
