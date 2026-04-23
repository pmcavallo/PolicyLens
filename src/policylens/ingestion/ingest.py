"""Ingestion orchestrator for PolicyLens.

Parses all PDFs, chunks them with section-aware metadata, and indexes
into ChromaDB with two collections (regulatory_frameworks, internal_policies).

Usage:
    py -m src.policylens.ingestion.ingest              # Full ingestion
    py -m src.policylens.ingestion.ingest --reset       # Clear and re-ingest
    py -m src.policylens.ingestion.ingest --stats       # Show collection stats
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.policylens.ingestion.pdf_parser import parse_all_pdfs
from src.policylens.ingestion.chunker import chunk_all_documents
from src.policylens.ingestion.vectorstore import (
    get_client,
    index_chunks,
    get_collection_stats,
    reset_collections,
    DEFAULT_PERSIST_DIR,
)


def ingest(
    data_dir: Path,
    persist_dir: Path = DEFAULT_PERSIST_DIR,
    reset: bool = False,
) -> dict[str, int]:
    """Run the full ingestion pipeline.

    Args:
        data_dir: Root data directory with frameworks/ and internal/ subdirs.
        persist_dir: ChromaDB persistence directory.
        reset: If True, delete existing collections before ingesting.

    Returns:
        Dict with ingestion statistics.
    """
    print("=" * 60)
    print("PolicyLens Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Parse PDFs
    print("\n[1/3] Parsing PDFs...")
    documents = parse_all_pdfs(data_dir)
    total_sections = sum(len(d.sections) for d in documents)
    print(f"  Parsed {len(documents)} documents, {total_sections} sections")
    for doc in documents:
        print(f"    {doc.framework_name}: {len(doc.sections)} sections ({doc.corpus_type})")

    # Step 2: Chunk sections
    print("\n[2/3] Chunking sections...")
    chunks = chunk_all_documents(documents)
    external_count = sum(1 for c in chunks if c.metadata["corpus_type"] == "external")
    internal_count = sum(1 for c in chunks if c.metadata["corpus_type"] == "internal")
    print(f"  Created {len(chunks)} chunks ({external_count} external, {internal_count} internal)")

    # Step 3: Index into ChromaDB
    print("\n[3/3] Indexing into ChromaDB...")
    client = get_client(persist_dir)

    if reset:
        print("  Resetting existing collections...")
        reset_collections(client)

    indexed = index_chunks(client, chunks)
    print(f"  Indexed {indexed} chunks")

    # Final stats
    stats = get_collection_stats(client)
    print("\n" + "=" * 60)
    print("Ingestion Complete")
    print("=" * 60)
    print(f"  regulatory_frameworks: {stats.get('regulatory_frameworks', 0)} chunks")
    print(f"  internal_policies:     {stats.get('internal_policies', 0)} chunks")
    print(f"  Total:                 {sum(stats.values())} chunks")

    return {
        "documents": len(documents),
        "sections": total_sections,
        "chunks": len(chunks),
        "indexed": indexed,
        **stats,
    }


def show_stats(persist_dir: Path = DEFAULT_PERSIST_DIR) -> None:
    """Display current collection statistics."""
    client = get_client(persist_dir)
    stats = get_collection_stats(client)
    print("ChromaDB Collection Stats:")
    for name, count in stats.items():
        print(f"  {name}: {count} chunks")
    print(f"  Total: {sum(stats.values())} chunks")


def main() -> None:
    parser = argparse.ArgumentParser(description="PolicyLens Ingestion Pipeline")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Root data directory (default: data/)",
    )
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=DEFAULT_PERSIST_DIR,
        help="ChromaDB persistence directory (default: data/chromadb/)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing collections before ingesting",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show collection stats and exit",
    )

    args = parser.parse_args()

    if args.stats:
        show_stats(args.persist_dir)
        return

    ingest(args.data_dir, args.persist_dir, args.reset)


if __name__ == "__main__":
    main()
