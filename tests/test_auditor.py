"""Tests for the ExecutionAuditor to ensure synthetic logs meet compliance."""

import json
from pathlib import Path

import pytest

from src.policylens.core.auditor import ExecutionAuditor


# Define mock models strictly according to the AGENTS.md synthetic data rules
class MockRiskTier:
    def __init__(self, value: str):
        self.value = value


class MockRiskAssessment:
    def __init__(self, risk_tier_value: str, gap_summary_list: list):
        self.risk_tier = MockRiskTier(risk_tier_value)
        self.gap_summary = gap_summary_list


def test_auditor_creates_log_file_and_logs_correctly(tmp_path: Path):
    """Test that the ExecutionAuditor writes the correct structured JSONL."""
    log_file = tmp_path / "logs" / "synthetic_audit_trail.jsonl"
    auditor = ExecutionAuditor(log_file=log_file)

    @auditor.audit_execution
    def mock_assessment_func(use_case: str):
        # Return a dummy MockRiskAssessment simulating a critical use case
        # for "Acme Synthetic Bank"
        return MockRiskAssessment(
            risk_tier_value="Critical",
            gap_summary_list=["gap1", "gap2", "gap3"]
        )

    # Execute the mock function
    use_case_desc = "Credit decisioning at Acme Synthetic Bank"
    result = mock_assessment_func(use_case_desc)

    # Ensure the original function returned correctly
    assert result.risk_tier.value == "Critical"
    assert len(result.gap_summary) == 3

    # Check that the log file was created
    assert log_file.exists()

    # Read the log file contents
    with open(log_file, "r") as f:
        lines = f.readlines()

    assert len(lines) == 1

    log_entry = json.loads(lines[0].strip())

    # Verify JSON structure
    assert "timestamp" in log_entry
    assert "execution_id" in log_entry
    assert "risk_tier" in log_entry
    assert "gap_count" in log_entry
    assert "policy_id" in log_entry

    # Verify execution ID format and synthetic data compliance
    assert log_entry["execution_id"].startswith("SYNTH-AUDIT-")

    # Verify correct data extraction
    assert log_entry["risk_tier"] == "Critical"
    assert log_entry["gap_count"] == 3
    assert log_entry["policy_id"] == "POL-ACME-001"


def test_auditor_handles_missing_attributes(tmp_path: Path):
    """Test that the ExecutionAuditor safely handles missing attributes on returned objects."""
    log_file = tmp_path / "logs" / "synthetic_audit_trail_fallback.jsonl"
    auditor = ExecutionAuditor(log_file=log_file)

    @auditor.audit_execution
    def mock_broken_assessment_func():
        # Return an empty dict which lacks risk_tier and gap_summary
        return {}

    result = mock_broken_assessment_func()
    assert result == {}

    with open(log_file, "r") as f:
        log_entry = json.loads(f.readlines()[0].strip())

    # Should fallback to UNKNOWN and 0
    assert log_entry["risk_tier"] == "UNKNOWN"
    assert log_entry["gap_count"] == 0
    assert log_entry["policy_id"] == "POL-ACME-001"
    assert log_entry["execution_id"].startswith("SYNTH-AUDIT-")
