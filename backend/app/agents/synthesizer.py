from app.core.llm_client import UnifiedLLM
from app.models.state import AgentState
from app.core.config import settings
import json
import re


def synthesizer_agent(state: AgentState) -> AgentState:
    """Generate summary and extract timeline events"""
    print(f"[Synthesizer] Creating summary and timeline...")

    if not state["analysis_results"]:
        state["errors"].append("No analysis results to synthesize")
        return state

    try:
        llm = UnifiedLLM(temperature=0.5)

        analysis = state["analysis_results"].get("raw_analysis", "")
        doc_type = state["document_type"]
        
        # Generate summary
        summary_prompt = f"""Based on this {doc_type} analysis, create a concise 2-3 sentence summary:

{analysis}

Summary:"""

        summary_response = llm.invoke(summary_prompt)
        state["summary"] = summary_response.content.strip()
        
        # Extract timeline events
        timeline_prompt = f"""Extract timeline events from this document analysis. 
For each event, provide:
- date (YYYY-MM-DD format, or "unknown" if not specified)
- event (brief description)
- type (one of: created, signed, payment_due, deadline, meeting, other)

Analysis:
{analysis}

Respond with JSON array format:
[{{"date": "2024-01-15", "event": "Invoice issued", "type": "created"}}]

If no dates found, return empty array: []"""

        timeline_response = llm.invoke(timeline_prompt)
        
        # Parse timeline events
        try:
            # Extract JSON from response
            content = timeline_response.content.strip()
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                events = json.loads(json_match.group())
                state["timeline_events"] = events
            else:
                state["timeline_events"] = []
        except:
            state["timeline_events"] = []
        
        state["current_agent"] = "synthesizer"
        
        print(f"[Synthesizer] Summary created, {len(state['timeline_events'])} events extracted")
        
    except Exception as e:
        state["errors"].append(f"Synthesis error: {str(e)}")
        state["summary"] = "Error generating summary"
        state["timeline_events"] = []
        print(f"[Synthesizer] Error: {e}")
    
    return state
