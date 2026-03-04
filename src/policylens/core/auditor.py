"""Auditor class to record assessment execution outcomes."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable

# Standard log path per requirements
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "synthetic_audit_trail.jsonl"


class ExecutionAuditor:
    """Wraps policy evaluations to securely log high-level execution outcomes."""

    def __init__(self, log_file: Path = LOG_FILE) -> None:
        self.log_file = log_file
        self.logger = self._configure_logger()

    def _configure_logger(self) -> logging.Logger:
        """Sets up a specific logger to write JSONL to the target log file."""
        # Use a unique logger name per file path to avoid caching handlers across tests
        logger = logging.getLogger(f"ExecutionAuditor_{self.log_file.name}")
        logger.setLevel(logging.INFO)

        # Remove existing handlers to ensure we write to the correct file
        if logger.hasHandlers():
            logger.handlers.clear()

        # Ensure the logs directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Use FileHandler for standard appending
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        # No specific format string needed since we will log raw JSON strings
        logger.addHandler(file_handler)

        return logger

    def audit_execution(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to audit the execution of an assessment function."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate synthetic execution ID
            exec_id = f"SYNTH-AUDIT-{uuid.uuid4()}"

            try:
                # Execute the actual function
                result = func(*args, **kwargs)

                # Assume the result is a RiskAssessment object
                risk_tier = getattr(result, "risk_tier", "UNKNOWN")
                if hasattr(risk_tier, "value"):
                    risk_tier = risk_tier.value

                gap_summary = getattr(result, "gap_summary", [])
                gap_count = len(gap_summary)

                # Build the high-level summary dictionary
                audit_record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "execution_id": exec_id,
                    "risk_tier": risk_tier,
                    "gap_count": gap_count,
                    # TODO: Schema doesn't currently contain a specific Policy ID.
                    # Hardcoded dummy ID. Will be updated in a future PR when schema is updated.
                    "policy_id": "POL-ACME-001"
                }

                # Log as JSON line
                self.logger.info(json.dumps(audit_record))

                return result

            except Exception as e:
                # Still might want to log failures, but requirements specifically
                # asked for the final evaluation outcome. Re-raise after logging?
                # For now, let exceptions propagate naturally.
                raise

        return wrapper

# Provide the default instance decorator for easy import
auditor = ExecutionAuditor()
audit_execution = auditor.audit_execution
