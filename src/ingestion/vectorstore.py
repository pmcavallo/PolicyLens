"""ChromaDB vector store with two collections for regulatory and internal documents.

Architecture from PROJECT_PLAN.md:
  - Collection 1: regulatory_frameworks (NIST AI 100-1, 600-1, FHFA AB 2022-02, SR 11-7)
  - Collection 2: internal_policies (Meridian AI Governance, Meridian MRM)

Queries run against BOTH collections to enable gap analysis between external
requirements and internal policy coverage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

from src.ingestion.chunker import Chunk


# Collection names matching the two-layer architecture
REGULATORY_COLLECTION = "regulatory_frameworks"
INTERNAL_COLLECTION = "internal_policies"

# Default embedding function: ChromaDB's built-in all-MiniLM-L6-v2
# This avoids needing sentence-transformers as a direct dependency at import time
DEFAULT_PERSIST_DIR = Path("data/chromadb")


def get_client(persist_dir: Path = DEFAULT_PERSIST_DIR) -> chromadb.ClientAPI:
    """Create or connect to a persistent ChromaDB client.

    Args:
        persist_dir: Directory for ChromaDB persistence.

    Returns:
        ChromaDB client instance.
    """
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def _get_or_create_collection(
    client: chromadb.ClientAPI,
    name: str,
) -> chromadb.Collection:
    """Get or create a ChromaDB collection with default embedding function."""
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(
    client: chromadb.ClientAPI,
    chunks: list[Chunk],
    collection_name: Optional[str] = None,
    batch_size: int = 100,
) -> int:
    """Index chunks into the appropriate ChromaDB collection.

    If collection_name is not specified, chunks are automatically routed
    based on their corpus_type metadata (external -> regulatory_frameworks,
    internal -> internal_policies).

    Args:
        client: ChromaDB client.
        chunks: List of chunks to index.
        collection_name: Override collection name (optional).
        batch_size: Number of chunks to add per batch.

    Returns:
        Number of chunks indexed.
    """
    if collection_name:
        # All chunks go to the specified collection
        collection = _get_or_create_collection(client, collection_name)
        return _add_chunks_to_collection(collection, chunks, batch_size)

    # Auto-route by corpus_type
    external_chunks = [c for c in chunks if c.metadata["corpus_type"] == "external"]
    internal_chunks = [c for c in chunks if c.metadata["corpus_type"] == "internal"]

    total = 0
    if external_chunks:
        reg_collection = _get_or_create_collection(client, REGULATORY_COLLECTION)
        total += _add_chunks_to_collection(reg_collection, external_chunks, batch_size)

    if internal_chunks:
        int_collection = _get_or_create_collection(client, INTERNAL_COLLECTION)
        total += _add_chunks_to_collection(int_collection, internal_chunks, batch_size)

    return total


def _add_chunks_to_collection(
    collection: chromadb.Collection,
    chunks: list[Chunk],
    batch_size: int,
) -> int:
    """Add chunks to a collection in batches."""
    total = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        # ChromaDB requires string values for metadata; convert None to ""
        clean_metadata = []
        for chunk in batch:
            meta = {}
            for k, v in chunk.metadata.items():
                if v is None:
                    meta[k] = ""
                else:
                    meta[k] = v
            clean_metadata.append(meta)

        collection.add(
            ids=[c.chunk_id for c in batch],
            documents=[c.text for c in batch],
            metadatas=clean_metadata,
        )
        total += len(batch)
    return total


def query_collection(
    client: chromadb.ClientAPI,
    collection_name: str,
    query_text: str,
    n_results: int = 10,
    where: Optional[dict] = None,
) -> dict:
    """Query a collection and return results with metadata.

    Args:
        client: ChromaDB client.
        collection_name: Name of the collection to query.
        query_text: The query string.
        n_results: Number of results to return.
        where: Optional metadata filter (e.g., {"rmf_function": "Govern"}).

    Returns:
        Dict with keys: ids, documents, metadatas, distances.
    """
    collection = client.get_collection(name=collection_name)

    query_params = {
        "query_texts": [query_text],
        "n_results": n_results,
    }
    if where:
        query_params["where"] = where

    return collection.query(**query_params)


def query_both_collections(
    client: chromadb.ClientAPI,
    query_text: str,
    n_results: int = 10,
    where: Optional[dict] = None,
) -> dict[str, dict]:
    """Query both regulatory and internal collections.

    This is the core retrieval pattern for gap analysis: get what regulation
    requires AND what internal policy says about the same topic.

    Args:
        client: ChromaDB client.
        query_text: The query string.
        n_results: Number of results per collection.
        where: Optional metadata filter.

    Returns:
        Dict with "external" and "internal" keys, each containing query results.
    """
    results = {}

    try:
        results["external"] = query_collection(
            client, REGULATORY_COLLECTION, query_text, n_results, where
        )
    except Exception:
        results["external"] = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    try:
        results["internal"] = query_collection(
            client, INTERNAL_COLLECTION, query_text, n_results, where
        )
    except Exception:
        results["internal"] = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    return results


def get_collection_stats(client: chromadb.ClientAPI) -> dict[str, int]:
    """Get document counts for both collections."""
    stats = {}
    for name in (REGULATORY_COLLECTION, INTERNAL_COLLECTION):
        try:
            collection = client.get_collection(name=name)
            stats[name] = collection.count()
        except Exception:
            stats[name] = 0
    return stats


def reset_collections(client: chromadb.ClientAPI) -> None:
    """Delete and recreate both collections. Use for re-ingestion."""
    for name in (REGULATORY_COLLECTION, INTERNAL_COLLECTION):
        try:
            client.delete_collection(name=name)
        except Exception:
            pass
