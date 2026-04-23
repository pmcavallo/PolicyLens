# PolicyLens

**AI Risk Assessment Engine for Financial Services**

PolicyLens operationalizes NIST AI 100-1, NIST AI 600-1, FHFA AB 2022-02, and SR 11-7 into structured governance assessments. Describe an AI use case, and it produces a Risk Committee-ready assessment organized by the NIST AI RMF's four functions (Govern, Map, Measure, Manage), with regulatory citations, internal policy alignment scoring, and a gap analysis identifying where institutional governance falls short of regulatory expectations.

> **Data Disclaimer:** All internal company documentation references Meridian Financial Group, a fictitious entity created for demonstration purposes. All data is synthetic. No real institution's policies or proprietary data are used.

---

## The Problem

Financial institutions deploying AI face a growing web of regulatory expectations: the NIST AI Risk Management Framework, FHFA Advisory Bulletin 2022-02, SR 11-7 model risk guidance, and emerging GenAI-specific requirements. Second-line risk teams must assess each AI use case against these frameworks, cross-reference their own internal governance policies, and document gaps with specific citations. This process is manual, inconsistent, and difficult to scale across an enterprise.

## The Methodology

PolicyLens implements a **three-layer compliance assessment model**:

```
Layer 1: External Regulation     "What does regulation REQUIRE?"
         (NIST AI 100-1, NIST AI 600-1, FHFA AB 2022-02, SR 11-7)
                    |
                    v  gap analysis
Layer 2: Internal Policy          "What does OUR POLICY cover?"
         (Institutional AI governance & MRM documentation)
                    |
                    v  use case assessment
Layer 3: Specific Use Case        "Does THIS deployment comply?"
         (User-described AI system)
```

For each use case, the engine:

1. **Classifies risk tier** (Critical / High / Medium / Low) based on decision impact, population affected, data sensitivity, autonomy level, and GenAI involvement
2. **Retrieves regulatory requirements** via section-aware RAG across four ingested frameworks
3. **Retrieves internal policy coverage** from a separate document collection
4. **Generates structured findings** organized by NIST AI RMF function, with specific section citations
5. **Identifies compliance gaps** where internal governance falls short of external requirements
6. **Produces remediation priorities** sorted by severity with actionable recommendations

## Sample Output

The assessment for an XGBoost credit decisioning model using alternative data (classified as **Critical** risk tier) identifies:

| Severity | Gaps Found | Example |
|----------|-----------|---------|
| Critical | 7 | No GenAI-specific provisions in governance framework |
| High | 1 | Monitoring language too vague for high-risk decisioning |

Coverage scores by RMF function: Govern 42.9%, Map 37.5%, Measure 33.3%, Manage 50.0%

The full sample report is available at [`examples/sample_report_credit_decisioning.md`](examples/sample_report_credit_decisioning.md).

## Frameworks Covered

| Framework | Source | Role in Assessment |
|-----------|--------|-------------------|
| **NIST AI 100-1** (AI RMF v1.0) | nist.gov | Primary structural backbone -- Govern, Map, Measure, Manage |
| **NIST AI 600-1** (GenAI Profile) | nist.gov | GenAI-specific risk overlay (hallucination, data leakage, etc.) |
| **FHFA AB 2022-02** | fhfa.gov | Financial services AI/ML risk management requirements |
| **SR 11-7** | federalreserve.gov | Model Risk Management foundation (Fed/OCC guidance) |

## Features

- **Section-aware RAG** -- Regulatory documents are parsed preserving their hierarchical structure (not naive fixed-window chunking), so every retrieval carries its full section lineage for precise citations
- **Dual-collection retrieval** -- Queries run against both regulatory frameworks and internal policy collections simultaneously, enabling cross-reference gap analysis
- **Pydantic-validated output** -- Every assessment is structurally validated: four RMF functions present, all findings carry citations, severity enums enforced
- **Risk Committee report export** -- Generates markdown reports in the format a second-line risk team would present to a governance committee
- **Interactive Streamlit UI** -- Tabbed dashboard with coverage scores, detailed findings, gap analysis table, and SR 11-7 alignment view
- **Pre-built demo cases** -- Four use cases (credit decisioning, GenAI chatbot, fraud detection, document summarization) demonstrate assessments across risk tiers

## Architecture

```
User Input (AI use case description)
        |
        v
Risk Tier Classifier (Claude API)
        |
        v
Dual-Collection RAG Retrieval (ChromaDB)
  - regulatory_frameworks (251 chunks from 4 documents)
  - internal_policies (45 chunks from 2 documents)
        |
        v
Assessment Generator (Claude API + structured prompt)
        |
        v
Post-Processing (coverage scoring, gap sorting, citation collection)
        |
        v
Output: Streamlit UI / Executive Report / JSON
```

## Tech Stack

| Component | Tool |
|-----------|------|
| Language | Python 3.10 |
| Vector Store | ChromaDB (dual collections, cosine similarity) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Claude API (claude-sonnet-4-5) |
| PDF Parsing | PyMuPDF |
| Output Validation | Pydantic |
| UI | Streamlit |

## Setup

```bash
# Clone and enter the project
git clone https://github.com/pmcavallo/PolicyLens.git
cd PolicyLens

# Create virtual environment
py -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API key
copy .env.example .env
# Edit .env and add your Anthropic API key
```

### Download Regulatory Frameworks

The four regulatory PDFs are not included in the repository due to file size. Download them into `data/frameworks/`:

| File | Source |
|------|--------|
| `NIST_AI_100-1.pdf` | [nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) |
| `NIST_AI_600-1.pdf` | [airc.nist.gov/Docs/1/handle](https://airc.nist.gov/Docs/1/handle) |
| `FHFA_AB_2022-02.pdf` | Search [fhfa.gov](https://www.fhfa.gov) for "Advisory Bulletin 2022-02" |
| `SR_11-7.pdf` | [federalreserve.gov/supervisionreg/srletters/sr1107a1.pdf](https://www.federalreserve.gov/supervisionreg/srletters/sr1107a1.pdf) |

## Usage

### 1. Ingest Documents

Parse PDFs, chunk with section metadata, and index into ChromaDB:

```bash
py -m src.policylens.ingestion.ingest
```

Options: `--reset` (clear and rebuild), `--stats` (show collection statistics)

### 2. Run Assessment (CLI)

```bash
py -m src.policylens.assessment.engine
```

Runs the credit decisioning demo case and prints a summary to the console.

### 3. Launch UI

```bash
streamlit run src/policylens/ui/app.py
```

The dashboard provides:
- Dropdown selection of pre-built demo cases or custom use case input
- Tabbed view across all four RMF functions with detailed findings
- Gap analysis table sorted by severity
- SR 11-7 alignment panel
- Export buttons for markdown report and raw JSON

## Project Structure

```
PolicyLens/
  data/
    frameworks/          # 4 regulatory PDFs (NIST, FHFA, SR 11-7)
    internal/            # 2 Meridian Financial Group policy PDFs
    chromadb/            # Vector store (generated by ingest)
  src/
    ingestion/
      pdf_parser.py      # Section-aware PDF parsing (6 document-specific parsers)
      chunker.py         # Section-level chunking with context prefixes
      vectorstore.py     # ChromaDB dual-collection management
      ingest.py          # CLI orchestrator
    assessment/
      classifier.py      # Risk tier classification
      prompts.py         # Assessment prompt template
      engine.py          # Pipeline orchestrator
      gap_analyzer.py    # Post-processing (coverage scores, gap sorting)
      schemas.py         # Pydantic models for structured output
    output/
      report.py          # Executive report generator
    ui/
      app.py             # Streamlit dashboard
      demo_cases.py      # Pre-built use case presets
  examples/
    demo1_credit_decisioning.json
    demo2_genai_chatbot.json
    sample_report_credit_decisioning.md
  tests/
```

---

**Author:** Paulo Cavallo

**Note:** This project was built as a portfolio demonstration of applied AI governance methodology. The regulatory frameworks are publicly available government documents. All internal policy content is synthetic.
