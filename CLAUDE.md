# PolicyLens - Claude Code Context

## What This Is
AI Risk Assessment Engine for financial services. Ingests 4 regulatory frameworks + 2 fictional internal policies (Meridian Financial Group) into dual ChromaDB collections, then produces structured risk assessments with gap analysis organized by NIST AI RMF functions.

**All Meridian Financial Group data is FICTIONAL and SYNTHETIC. No real institution data.**

## Tech Stack
- Python 3.10, PyMuPDF, ChromaDB, Anthropic Claude API, Pydantic, Streamlit, sentence-transformers
- LLM model: `claude-sonnet-4-5-20250929`
- Embeddings: `all-MiniLM-L6-v2` (via ChromaDB default)

## Architecture
1. **Ingestion** (`src/ingestion/`): PDF parse → section-aware chunk → ChromaDB index
2. **Assessment** (`src/assessment/`): Classify risk tier → dual RAG retrieval → LLM structured output → post-processing gap analysis
3. **Output** (`src/output/`): Executive report generator (markdown)
4. **UI** (`src/ui/`): Streamlit dashboard with 8 tabs

## Key Files
- `src/ingestion/pdf_parser.py` - 6 document-specific parsers with regex patterns per framework
- `src/ingestion/chunker.py` - Section-level chunking with context prefixes (not fixed-window)
- `src/ingestion/vectorstore.py` - Dual ChromaDB collections: `regulatory_frameworks`, `internal_policies`
- `src/ingestion/ingest.py` - CLI: `py -m src.policylens.ingestion.ingest [--reset] [--stats]`
- `src/assessment/schemas.py` - Pydantic models: RiskAssessment, RMFFunctionAssessment, GapFinding, etc.
- `src/assessment/classifier.py` - Risk tier classifier (Critical/High/Medium/Low)
- `src/assessment/prompts.py` - System prompt + assessment prompt template
- `src/assessment/engine.py` - Pipeline orchestrator. CLI: `py -m src.policylens.assessment.engine`
- `src/assessment/gap_analyzer.py` - Post-processing: coverage scores, gap sorting, citation collection
- `src/output/report.py` - Executive report generator (Risk Committee format)
- `src/ui/app.py` - Streamlit UI. Run: `py -m streamlit run src/policylens/ui/app.py`
- `src/ui/demo_cases.py` - 4 pre-built demo use cases
- `PROJECT_PLAN.md` - Full architecture spec, intentional gaps list, positioning guidance

## How to Run
```bash
# Activate venv
.venv\Scripts\activate

# Ingest documents (only needed once, or after --reset)
py -m src.policylens.ingestion.ingest

# Run assessment from CLI
py -m src.policylens.assessment.engine

# Launch Streamlit UI
py -m streamlit run src/policylens/ui/app.py
```

## Data Layout
- `data/frameworks/` - 4 regulatory PDFs (NIST AI 100-1, NIST AI 600-1, FHFA AB 2022-02, SR 11-7)
- `data/internal/` - 2 Meridian policy PDFs (AI Governance, MRM)
- `data/chromadb/` - Generated vector store (251 external + 45 internal chunks)
- `examples/` - Demo assessment JSON outputs and sample report

## Important Details
- `.env` must contain `ANTHROPIC_API_KEY` (uses `load_dotenv(override=True)`)
- Assessment uses `max_tokens=16000` (full assessment JSON is large)
- Coverage score formula: ADEQUATE=100%, PARTIAL=50%, MISSING=0%
- Meridian policies have INTENTIONAL gaps (see PROJECT_PLAN.md "Summary of Intentional Gaps")
- 4 RMF functions always present: Govern, Map, Measure, Manage (enforced by Pydantic min_length=4, max_length=4)

## Constraints
- Never use real company names — Meridian Financial Group only
- Never fabricate metrics or performance numbers
- All output must state data is synthetic
- Do not modify files in `data/frameworks/` or `data/internal/` (source PDFs)
