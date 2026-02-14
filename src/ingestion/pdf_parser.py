"""Section-aware PDF parser for regulatory and internal policy documents.

Extracts text from PDFs while preserving section hierarchy. Each document
type has specific section-header patterns (NIST RMF functions, Roman numerals,
numbered sections) that are detected and used to split content into structured
sections with full metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# Document registry – maps filenames to metadata
# ---------------------------------------------------------------------------

DOCUMENT_REGISTRY: dict[str, dict[str, str]] = {
    "NIST.AI.100-1.pdf": {
        "framework_name": "NIST AI 100-1",
        "document_type": "framework",
        "corpus_type": "external",
    },
    "NIST.AI.600-1.pdf": {
        "framework_name": "NIST AI 600-1",
        "document_type": "framework",
        "corpus_type": "external",
    },
    "ab-2022-02.pdf": {
        "framework_name": "FHFA AB 2022-02",
        "document_type": "advisory_bulletin",
        "corpus_type": "external",
    },
    "sr1107a1.pdf": {
        "framework_name": "SR 11-7",
        "document_type": "supervisory_guidance",
        "corpus_type": "external",
    },
    "Meridian_AI_ML_Governance_Policy.pdf": {
        "framework_name": "Meridian AI Governance Policy",
        "document_type": "internal_policy",
        "corpus_type": "internal",
    },
    "Meridian_MRM_Policy.pdf": {
        "framework_name": "Meridian MRM Policy",
        "document_type": "internal_policy",
        "corpus_type": "internal",
    },
}


# ---------------------------------------------------------------------------
# RMF function mapping for NIST documents
# ---------------------------------------------------------------------------

def _rmf_function_from_section_id(section_id: str) -> Optional[str]:
    """Derive the RMF function (Govern/Map/Measure/Manage) from a section ID."""
    upper = section_id.upper()
    for func in ("GOVERN", "MAP", "MEASURE", "MANAGE"):
        if upper.startswith(func):
            return func.capitalize()
    return None


def _rmf_category_from_section_id(section_id: str) -> Optional[str]:
    """Extract parent category, e.g. 'GOVERN 1' from 'GOVERN 1.3'."""
    m = re.match(r"^((?:GOVERN|MAP|MEASURE|MANAGE)\s+\d+)", section_id, re.IGNORECASE)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Section heading detection patterns
# ---------------------------------------------------------------------------

# NIST AI 100-1 / 600-1: "GOVERN 1.1:", "MAP 2.3:", etc.
_RE_NIST_RMF = re.compile(
    r"^((?:GOVERN|MAP|MEASURE|MANAGE)\s+\d+(?:\.\d+)?)\s*[:\.]?\s*(.*)",
    re.IGNORECASE,
)

# FHFA AB 2022-02: Roman numeral sections "I.", "II.", "III." (top-level)
_RE_ROMAN = re.compile(
    r"^([IVX]+)\.\s*(.*)",
)

# FHFA sub-sections: "A. Roles and Responsibilities"
_RE_ALPHA_SUB = re.compile(
    r"^([A-Z])\.\s+(.*)",
)

# SR 11-7: All-caps Roman numeral headers "III. OVERVIEW OF MODEL RISK MANAGEMENT"
_RE_SR_ROMAN = re.compile(
    r"^([IVX]+)\.\s+([A-Z][A-Z\s,]+)$",
)

# Internal Meridian docs: "1. Purpose", "2.1 Data Quality", "3.2.1 Sub-detail"
# Top-level: "1. Purpose" (number + period + space)
_RE_NUMBERED_TOP = re.compile(
    r"^(\d+)\.\s+(.*)",
)
# Subsection: "1.1 Definition", "2.1 AI Risk" (number.number + space, no trailing period)
_RE_NUMBERED_SUB = re.compile(
    r"^(\d+\.\d+(?:\.\d+)*)\s+(.*)",
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ParsedSection:
    """A single section extracted from a PDF."""
    section_id: str
    section_title: str
    parent_section: Optional[str]
    content: str
    page_start: int
    page_end: int
    # Metadata populated after parsing
    framework_name: str = ""
    document_type: str = ""
    corpus_type: str = ""
    rmf_function: Optional[str] = None


@dataclass
class ParsedDocument:
    """A fully parsed PDF document."""
    filename: str
    framework_name: str
    document_type: str
    corpus_type: str
    total_pages: int
    sections: list[ParsedSection] = field(default_factory=list)
    raw_text: str = ""


# ---------------------------------------------------------------------------
# Parser implementations per document type
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    """Normalize whitespace and remove common PDF artifacts."""
    # Remove page headers/footers that repeat
    text = re.sub(r"^Page \d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^CONFIDENTIAL.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^Meridian Financial Group \|.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^AB 2022-02.*?Page \d+\s*$", "", text, flags=re.MULTILINE)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_full_text(doc: fitz.Document) -> list[tuple[int, str]]:
    """Extract text per page, returning list of (page_number, cleaned_text)."""
    pages: list[tuple[int, str]] = []
    for i in range(len(doc)):
        raw = doc[i].get_text()
        cleaned = _clean_text(raw)
        if cleaned:
            pages.append((i + 1, cleaned))
    return pages


def _try_numbered_match(stripped: str) -> tuple[str, str] | None:
    """Try to match a numbered section header. Returns (section_id, title) or None."""
    # Try top-level first: "1. Purpose and Scope"
    m = _RE_NUMBERED_TOP.match(stripped)
    if m and len(stripped) < 120:
        return m.group(1), m.group(2).strip()
    # Try subsection: "1.1 Definition of AI/ML Model"
    m = _RE_NUMBERED_SUB.match(stripped)
    if m and len(stripped) < 120:
        return m.group(1), m.group(2).strip()
    return None


def _parse_nist_100(pages: list[tuple[int, str]], meta: dict[str, str]) -> list[ParsedSection]:
    """Parse NIST AI 100-1 using GOVERN/MAP/MEASURE/MANAGE patterns.

    The core RMF subcategories appear in tables on pages ~27-38.
    Earlier pages contain Part 1 foundational information parsed with
    numbered section patterns.
    """
    sections: list[ParsedSection] = []
    current_section: Optional[ParsedSection] = None

    for page_num, text in pages:
        lines = text.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            match = _RE_NIST_RMF.match(stripped)
            if match:
                # Save previous section
                if current_section:
                    sections.append(current_section)

                section_id = match.group(1).upper()
                title = match.group(2).strip()
                parent = _rmf_category_from_section_id(section_id)
                rmf_func = _rmf_function_from_section_id(section_id)

                current_section = ParsedSection(
                    section_id=section_id,
                    section_title=title,
                    parent_section=parent,
                    content="",
                    page_start=page_num,
                    page_end=page_num,
                    framework_name=meta["framework_name"],
                    document_type=meta["document_type"],
                    corpus_type=meta["corpus_type"],
                    rmf_function=rmf_func,
                )
                if title:
                    current_section.content = title + "\n"
                continue

            # If we're inside a section, accumulate content
            if current_section:
                current_section.content += stripped + "\n"
                current_section.page_end = page_num
            else:
                # Pre-RMF content: Part 1 foundational info
                # Create sections based on numbered headings or just accumulate
                num_result = _try_numbered_match(stripped)
                if num_result and len(stripped) < 100:
                    if current_section:
                        sections.append(current_section)
                    sec_id, title = num_result
                    parent = sec_id.rsplit(".", 1)[0] if "." in sec_id else None
                    current_section = ParsedSection(
                        section_id=f"Part 1, {sec_id}",
                        section_title=title,
                        parent_section=parent,
                        content=title + "\n",
                        page_start=page_num,
                        page_end=page_num,
                        framework_name=meta["framework_name"],
                        document_type=meta["document_type"],
                        corpus_type=meta["corpus_type"],
                        rmf_function=None,
                    )

    if current_section:
        sections.append(current_section)

    return sections


def _parse_nist_600(pages: list[tuple[int, str]], meta: dict[str, str]) -> list[ParsedSection]:
    """Parse NIST AI 600-1 (GenAI Profile).

    Uses same GOVERN/MAP/MEASURE/MANAGE patterns as 100-1 but sections
    include GAI-specific suggested actions and risk tags.
    """
    # Same RMF patterns apply; reuse the 100-1 parser
    return _parse_nist_100(pages, meta)


def _parse_fhfa(pages: list[tuple[int, str]], meta: dict[str, str]) -> list[ParsedSection]:
    """Parse FHFA AB 2022-02 using Roman numeral + alpha sub-section patterns."""
    sections: list[ParsedSection] = []
    current_section: Optional[ParsedSection] = None
    current_top_roman: Optional[str] = None

    # Map Roman numerals to titles
    roman_titles: dict[str, str] = {}

    for page_num, text in pages:
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped:
                i += 1
                continue

            # Check for Roman numeral top-level header
            roman_match = _RE_ROMAN.match(stripped)
            if roman_match:
                numeral = roman_match.group(1)
                title = roman_match.group(2).strip()

                # Sometimes the title is on the next line
                if not title and i + 1 < len(lines):
                    title = lines[i + 1].strip()
                    i += 1

                if current_section:
                    sections.append(current_section)

                current_top_roman = numeral
                roman_titles[numeral] = title
                current_section = ParsedSection(
                    section_id=f"Section {numeral}",
                    section_title=title,
                    parent_section=None,
                    content=title + "\n" if title else "",
                    page_start=page_num,
                    page_end=page_num,
                    framework_name=meta["framework_name"],
                    document_type=meta["document_type"],
                    corpus_type=meta["corpus_type"],
                    rmf_function=None,
                )
                i += 1
                continue

            # Check for alpha sub-section: "A. Roles and Responsibilities"
            alpha_match = _RE_ALPHA_SUB.match(stripped)
            if alpha_match and current_top_roman:
                if current_section:
                    sections.append(current_section)

                letter = alpha_match.group(1)
                title = alpha_match.group(2).strip()
                parent = f"Section {current_top_roman}"

                current_section = ParsedSection(
                    section_id=f"Section {current_top_roman}.{letter}",
                    section_title=title,
                    parent_section=parent,
                    content=title + "\n",
                    page_start=page_num,
                    page_end=page_num,
                    framework_name=meta["framework_name"],
                    document_type=meta["document_type"],
                    corpus_type=meta["corpus_type"],
                    rmf_function=None,
                )
                i += 1
                continue

            # Accumulate content
            if current_section:
                current_section.content += stripped + "\n"
                current_section.page_end = page_num
            i += 1

    if current_section:
        sections.append(current_section)

    return sections


def _parse_sr117(pages: list[tuple[int, str]], meta: dict[str, str]) -> list[ParsedSection]:
    """Parse SR 11-7 using all-caps Roman numeral headers."""
    sections: list[ParsedSection] = []
    current_section: Optional[ParsedSection] = None

    # Skip page 1 which is a table of contents with fragmented section titles
    content_pages = [(pn, t) for pn, t in pages if pn > 1]

    for page_num, text in content_pages:
        lines = text.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # All-caps Roman numeral header
            sr_match = _RE_SR_ROMAN.match(stripped)
            if sr_match:
                if current_section:
                    sections.append(current_section)

                numeral = sr_match.group(1)
                title = sr_match.group(2).strip().title()

                current_section = ParsedSection(
                    section_id=f"Section {numeral}",
                    section_title=title,
                    parent_section=None,
                    content=title + "\n",
                    page_start=page_num,
                    page_end=page_num,
                    framework_name=meta["framework_name"],
                    document_type=meta["document_type"],
                    corpus_type=meta["corpus_type"],
                    rmf_function=None,
                )
                continue

            # Also catch non-caps Roman numeral patterns as fallback
            roman_match = _RE_ROMAN.match(stripped)
            if roman_match and len(stripped) < 80:
                title_text = roman_match.group(2).strip()
                # Only treat as section if it looks like a heading (short, mostly caps or title case)
                if title_text and not title_text[0].islower():
                    if current_section:
                        sections.append(current_section)

                    numeral = roman_match.group(1)
                    current_section = ParsedSection(
                        section_id=f"Section {numeral}",
                        section_title=title_text,
                        parent_section=None,
                        content=title_text + "\n",
                        page_start=page_num,
                        page_end=page_num,
                        framework_name=meta["framework_name"],
                        document_type=meta["document_type"],
                        corpus_type=meta["corpus_type"],
                        rmf_function=None,
                    )
                    continue

            if current_section:
                current_section.content += stripped + "\n"
                current_section.page_end = page_num

    if current_section:
        sections.append(current_section)

    return sections


def _parse_meridian(pages: list[tuple[int, str]], meta: dict[str, str]) -> list[ParsedSection]:
    """Parse Meridian internal policy docs using numbered section patterns."""
    sections: list[ParsedSection] = []
    current_section: Optional[ParsedSection] = None

    for page_num, text in pages:
        lines = text.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            result = _try_numbered_match(stripped)
            if result:
                sec_id, title = result

                # Skip version numbers like "1.0" or "2.1" when they appear
                # in document metadata context (no meaningful title)
                if not title or title.lower() in ("", "0"):
                    continue

                if current_section:
                    sections.append(current_section)

                # Determine parent: "2.1" -> parent is "2", "3.2.1" -> "3.2"
                parent = None
                if "." in sec_id:
                    parent_id = sec_id.rsplit(".", 1)[0]
                    parent = f"Section {parent_id}"

                current_section = ParsedSection(
                    section_id=f"Section {sec_id}",
                    section_title=title,
                    parent_section=parent,
                    content=title + "\n",
                    page_start=page_num,
                    page_end=page_num,
                    framework_name=meta["framework_name"],
                    document_type=meta["document_type"],
                    corpus_type=meta["corpus_type"],
                    rmf_function=None,
                )
                continue

            if current_section:
                current_section.content += stripped + "\n"
                current_section.page_end = page_num

    if current_section:
        sections.append(current_section)

    return sections


# ---------------------------------------------------------------------------
# Main parser dispatch
# ---------------------------------------------------------------------------

_PARSER_DISPATCH: dict[str, callable] = {
    "NIST.AI.100-1.pdf": _parse_nist_100,
    "NIST.AI.600-1.pdf": _parse_nist_600,
    "ab-2022-02.pdf": _parse_fhfa,
    "sr1107a1.pdf": _parse_sr117,
    "Meridian_AI_ML_Governance_Policy.pdf": _parse_meridian,
    "Meridian_MRM_Policy.pdf": _parse_meridian,
}


def _deduplicate_sections(sections: list[ParsedSection]) -> list[ParsedSection]:
    """When a TOC and body both produce sections with the same ID, keep the longer one."""
    seen: dict[str, int] = {}  # section_id -> index in result list
    result: list[ParsedSection] = []

    for section in sections:
        key = section.section_id
        if key in seen:
            existing_idx = seen[key]
            if len(section.content) > len(result[existing_idx].content):
                result[existing_idx] = section
        else:
            seen[key] = len(result)
            result.append(section)

    return result


def parse_pdf(pdf_path: Path) -> ParsedDocument:
    """Parse a PDF file into structured sections with metadata.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        ParsedDocument with sections, metadata, and raw text.

    Raises:
        ValueError: If the PDF filename is not in the document registry.
        FileNotFoundError: If the PDF does not exist.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    filename = pdf_path.name
    if filename not in DOCUMENT_REGISTRY:
        raise ValueError(
            f"Unknown document: {filename}. "
            f"Expected one of: {list(DOCUMENT_REGISTRY.keys())}"
        )

    meta = DOCUMENT_REGISTRY[filename]
    doc = fitz.open(str(pdf_path))

    try:
        pages = _extract_full_text(doc)
        raw_text = "\n\n".join(text for _, text in pages)

        parser_fn = _PARSER_DISPATCH[filename]
        sections = parser_fn(pages, meta)

        # Strip trailing whitespace from all section content
        for section in sections:
            section.content = section.content.strip()

        # Deduplicate sections: TOC pages often create stub entries with the
        # same section_id as the real content sections. Keep the longest.
        sections = _deduplicate_sections(sections)

        # Filter out sections with negligible content (just the title or less)
        sections = [
            s for s in sections
            if len(s.content) > len(s.section_title) + 10
        ]

        return ParsedDocument(
            filename=filename,
            framework_name=meta["framework_name"],
            document_type=meta["document_type"],
            corpus_type=meta["corpus_type"],
            total_pages=len(doc),
            sections=sections,
            raw_text=raw_text,
        )
    finally:
        doc.close()


def parse_all_pdfs(data_dir: Path) -> list[ParsedDocument]:
    """Parse all registered PDFs from the data directory.

    Args:
        data_dir: Root data directory containing frameworks/ and internal/ subdirs.

    Returns:
        List of ParsedDocument objects.
    """
    documents: list[ParsedDocument] = []
    for filename in DOCUMENT_REGISTRY:
        # Search in both subdirectories
        for subdir in ("frameworks", "internal"):
            candidate = data_dir / subdir / filename
            if candidate.exists():
                documents.append(parse_pdf(candidate))
                break
        else:
            print(f"WARNING: {filename} not found in {data_dir}")
    return documents
