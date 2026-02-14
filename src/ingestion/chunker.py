"""Section-aware chunking with metadata for ChromaDB ingestion.

Converts ParsedSections into chunks suitable for embedding and vector storage.
Each chunk carries full metadata (framework, section hierarchy, RMF function,
corpus type) and a context prefix for improved retrieval accuracy.

Chunks are created at the section level. Sections exceeding the max chunk size
are split at paragraph boundaries while preserving all metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.ingestion.pdf_parser import ParsedDocument, ParsedSection


# Default max chunk size in characters (~500 tokens at ~4 chars/token = 2000 chars)
DEFAULT_MAX_CHUNK_SIZE = 2000
# Minimum chunk size to avoid creating tiny fragments
MIN_CHUNK_SIZE = 100


@dataclass
class Chunk:
    """A single chunk ready for embedding and vector storage."""
    chunk_id: str
    text: str
    metadata: dict[str, str | int | None]


def _build_context_prefix(section: ParsedSection) -> str:
    """Build a context prefix for a chunk to improve retrieval.

    Format: [NIST AI 100-1 > Govern > GOVERN 1.1: Legal and Regulatory Requirements]
    """
    parts = [section.framework_name]
    if section.rmf_function:
        parts.append(section.rmf_function)
    if section.parent_section:
        parts.append(section.parent_section)
    parts.append(f"{section.section_id}: {section.section_title}")
    return f"[{' > '.join(parts)}]"


def _build_metadata(section: ParsedSection, chunk_index: int = 0) -> dict[str, str | int | None]:
    """Build metadata dict for a chunk."""
    return {
        "framework_name": section.framework_name,
        "section_id": section.section_id,
        "section_title": section.section_title,
        "parent_section": section.parent_section,
        "rmf_function": section.rmf_function,
        "document_type": section.document_type,
        "corpus_type": section.corpus_type,
        "page_start": section.page_start,
        "page_end": section.page_end,
        "chunk_index": chunk_index,
    }


def _split_at_paragraphs(text: str, max_size: int) -> list[str]:
    """Split text at paragraph boundaries (double newlines) to stay under max_size.

    Falls back to single newline splits if paragraphs are too large,
    and finally to hard character splits as a last resort.
    """
    if len(text) <= max_size:
        return [text]

    chunks: list[str] = []
    paragraphs = text.split("\n\n")

    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= max_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds max_size, split at sentences/lines
            if len(para) > max_size:
                lines = para.split("\n")
                current = ""
                for line in lines:
                    line_candidate = f"{current}\n{line}".strip() if current else line
                    if len(line_candidate) <= max_size:
                        current = line_candidate
                    else:
                        if current:
                            chunks.append(current)
                        # Hard split as last resort
                        while len(line) > max_size:
                            chunks.append(line[:max_size])
                            line = line[max_size:]
                        current = line
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def chunk_section(
    section: ParsedSection,
    doc_index: int,
    section_index: int,
    max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE,
) -> list[Chunk]:
    """Convert a ParsedSection into one or more Chunks.

    Args:
        section: The parsed section to chunk.
        doc_index: Index of the document (for generating unique chunk IDs).
        section_index: Index of the section within the document.
        max_chunk_size: Maximum character count per chunk.

    Returns:
        List of Chunk objects with metadata and context prefix.
    """
    prefix = _build_context_prefix(section)
    content = section.content.strip()

    if not content or len(content) < MIN_CHUNK_SIZE:
        return []

    # Account for prefix in size calculation
    effective_max = max_chunk_size - len(prefix) - 2  # 2 for newline separator
    text_parts = _split_at_paragraphs(content, effective_max)

    chunks: list[Chunk] = []
    for i, part in enumerate(text_parts):
        chunk_text = f"{prefix}\n{part}"
        chunk_id = f"doc{doc_index}_sec{section_index}_chunk{i}"
        chunks.append(Chunk(
            chunk_id=chunk_id,
            text=chunk_text,
            metadata=_build_metadata(section, chunk_index=i),
        ))

    return chunks


def chunk_document(
    document: ParsedDocument,
    doc_index: int = 0,
    max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE,
) -> list[Chunk]:
    """Convert all sections of a ParsedDocument into Chunks.

    Args:
        document: The parsed document.
        doc_index: Index of the document (for unique chunk IDs).
        max_chunk_size: Maximum character count per chunk.

    Returns:
        List of all Chunks from the document.
    """
    all_chunks: list[Chunk] = []
    for sec_idx, section in enumerate(document.sections):
        section_chunks = chunk_section(section, doc_index, sec_idx, max_chunk_size)
        all_chunks.extend(section_chunks)
    return all_chunks


def chunk_all_documents(
    documents: list[ParsedDocument],
    max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE,
) -> list[Chunk]:
    """Chunk all documents, returning a flat list of Chunks.

    Args:
        documents: List of parsed documents.
        max_chunk_size: Maximum character count per chunk.

    Returns:
        List of all Chunks across all documents.
    """
    all_chunks: list[Chunk] = []
    for doc_idx, doc in enumerate(documents):
        doc_chunks = chunk_document(doc, doc_idx, max_chunk_size)
        all_chunks.extend(doc_chunks)
    return all_chunks
