# Backend AI Agent Workflow

## Overview
The **Chronicles of Documents** backend uses a **LangGraph** workflow to orchestrate four specialized AI agents that process uploaded documents end‑to‑end:

1. **Extractor** – pulls raw text, tables and metadata from the file (PDF, DOCX, image, etc.).
2. **Classifier** – determines the document type (invoice, contract, letter, chat, …) using an LLM.
3. **Analyzer** – runs a type‑specific LLM prompt to extract structured information.
4. **Synthesizer** – creates a concise summary and a timeline of events from the analysis.

The agents share a common **state model** (`AgentState`) that is passed from one node to the next. The workflow is defined in `backend/app/agents/workflow.py` and compiled into a runnable graph.

---

## State Model (`AgentState`)
```python
class AgentState(TypedDict):
    document_id: str
    case_id: str
    user_id: str
    file_path: str
    file_type: str
    file_name: str
    extracted_text: str
    tables: list[dict]
    document_type: str | None
    classification_confidence: float | None
    analysis_results: dict
    summary: str
    timeline_events: list[dict]
    errors: list[str]
    current_agent: str
```
*Each agent reads from and writes to this dictionary, allowing the next agent to build on the previous results.*

---

## Agent Implementations

### 1. Extractor (`extractor.py`)
```python
from app.core.parsers_production import ProductionDocumentParser as DocumentParser

def extractor_agent(state: AgentState) -> AgentState:
    text, tables = DocumentParser.parse_document(state["file_path"])
    state["extracted_text"] = text
    state["tables"] = tables
    state["current_agent"] = "extractor"
    return state
```
* Uses `ProductionDocumentParser` (PDFPlumber, python‑docx, pytesseract, etc.) to read the file.
* Populates `extracted_text` and `tables`.
* Errors are appended to `state["errors"]`.

---

### 2. Classifier (`classifier.py`)
```python
from app.core.llm_client import UnifiedLLM

def classifier_agent(state: AgentState) -> AgentState:
    llm = UnifiedLLM(temperature=0)
    sample = state["extracted_text"][:2000]
    prompt = f"""Classify the following text into one of …\n\n{sample}\n\nRespond with:\ncategory: <name>\nconfidence: <0‑1>"""
    resp = llm.invoke(prompt)
    # parse response → state["document_type"], state["classification_confidence"]
    state["current_agent"] = "classifier"
    return state
```
* Sends a short excerpt (first 2 k characters) to the LLM.
* Expects a deterministic `category:` and `confidence:` line.
* Fallback to `generic` on error.

---

### 3. Analyzer (`analyzer.py`)
```python
from app.core.llm_client import UnifiedLLM

def analyzer_agent(state: AgentState) -> AgentState:
    llm = UnifiedLLM(temperature=0.3)
    prompts = {"invoice": "…", "contract": "…", "letter": "…", "chat": "…", "generic": "…"}
    prompt = prompts.get(state["document_type"], prompts["generic"]) + f"\n\nDocument text:\n{state["extracted_text"][:4000]}"
    resp = llm.invoke(prompt)
    state["analysis_results"] = {"type": state["document_type"], "raw_analysis": resp.content}
    state["current_agent"] = "analyzer"
    return state
```
* Chooses a type‑specific prompt that asks the LLM to output **JSON** with the fields relevant to that document type.
* Truncates the text to 4 k characters to stay within model limits.

---

### 4. Synthesizer (`synthesizer.py`)
```python
from app.core.llm_client import UnifiedLLM
import json, re

def synthesizer_agent(state: AgentState) -> AgentState:
    llm = UnifiedLLM(temperature=0.5)
    # Summary
    summary_prompt = f"Based on this {state['document_type']} analysis, create a concise 2‑3 sentence summary:\n{analysis}\nSummary:"
    summary = llm.invoke(summary_prompt).content.strip()
    # Timeline extraction
    timeline_prompt = f"Extract timeline events …\n{analysis}\nRespond with JSON array …"
    timeline_resp = llm.invoke(timeline_prompt).content
    match = re.search(r"\[.*\]", timeline_resp, re.S)
    events = json.loads(match.group()) if match else []
    state.update({"summary": summary, "timeline_events": events, "current_agent": "synthesizer"})
    return state
```
* Generates a short human‑readable summary.
* Extracts a list of dated events (JSON) for the case timeline.
* Errors are caught and result in empty summary / timeline.

---

## Workflow Graph (`workflow.py`)
```python
from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from .extractor import extractor_agent
from .classifier import classifier_agent
from .analyzer import analyzer_agent
from .synthesizer import synthesizer_agent

def create_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("extractor", extractor_agent)
    workflow.add_node("classifier", classifier_agent)
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "classifier")
    workflow.add_edge("classifier", "analyzer")
    workflow.add_edge("analyzer", "synthesizer")
    workflow.add_edge("synthesizer", END)
    return workflow.compile()
```
* Linear flow: **extract → classify → analyze → synthesize → END**.
* `StateGraph.compile()` returns a callable that the `ScanService` invokes for each document.

---

## Interaction with Services
* **`ScanService.start_scan`** creates a background task that iterates over all documents of a case and calls the compiled workflow for each file.
* The resulting `summary`, `timeline_events` and `analysis_results` are stored in the `analysis_results` MongoDB collection.
* Errors collected in `state["errors"]` are persisted for debugging and shown via the `/cases/{case_id}/scan/status` endpoint.

---

## File Lifecycle & TTL Cleanup
* Uploaded files are stored **temporarily** in GridFS (encrypted). The document metadata includes an `expires_at` field.
* MongoDB indexes (`expireAfterSeconds: 0`) automatically delete the raw file **after the configured retention period** (default 24 h, see `FILE_RETENTION_HOURS` in `.env`).
* Only the **extracted, anonymised insights** remain in the database, satisfying the PII protection policy.

---

## Summary
The backend AI pipeline is a clean, linear LangGraph workflow where each node is a pure function that mutates a shared `AgentState`.  This design makes the process:
* **Deterministic** – the order of execution is fixed.
* **Observable** – errors and intermediate results are stored in the state.
* **Scalable** – the workflow can be run in parallel for many documents via FastAPI background tasks.
* **Privacy‑first** – raw files are automatically removed after processing, leaving only structured, non‑PII data.

For any further deep‑dive (e.g., prompt tuning, adding a new document type, or visualising the graph), let me know!