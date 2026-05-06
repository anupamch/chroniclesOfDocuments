from app.core.llm_client import UnifiedLLM
from app.models.state import AgentState
from app.core.config import settings


def analyzer_agent(state: AgentState) -> AgentState:
    """Analyze document based on its type"""
    print(f"[Analyzer] Analyzing {state['document_type']} document...")

    if not state["extracted_text"]:
        state["errors"].append("No text to analyze")
        return state

    try:
        llm = UnifiedLLM(temperature=0.3)

        doc_type = state["document_type"]
        text = state["extracted_text"]

        # Type-specific analysis prompts
        prompts = {
            "invoice": """Extract key information from this invoice:
- Invoice number
- Date
- Total amount
- Currency
- Vendor/Supplier
- Line items count
- Payment terms

Format as JSON.""",
            
            "contract": """Extract key information from this contract:
- Contract type
- Parties involved (use generic names like Party A, Party B)
- Effective date
- Expiration date
- Key terms and obligations
- Payment terms

Format as JSON.""",
            
            "letter": """Extract key information from this letter:
- Date
- Subject/Purpose
- Key points
- Action items
- Tone (formal/informal)

Format as JSON.""",
            
            "chat": """Analyze this chat conversation:
- Number of participants
- Date range
- Main topics discussed
- Key decisions or action items
- Sentiment

Format as JSON.""",
            
            "generic": """Analyze this document and extract:
- Main topic
- Key points (list)
- Important dates
- Action items
- Document purpose

Format as JSON."""
        }
        
        prompt_template = prompts.get(doc_type, prompts["generic"])
        
        full_prompt = f"""{prompt_template}

Document text:
{text[:4000]}

Respond with valid JSON only."""

        response = llm.invoke(full_prompt)
        
        state["analysis_results"] = {
            "type": doc_type,
            "raw_analysis": response.content,
            "file_name": state["file_name"]
        }
        state["current_agent"] = "analyzer"
        
        print(f"[Analyzer] Analysis complete")
        
    except Exception as e:
        state["errors"].append(f"Analysis error: {str(e)}")
        print(f"[Analyzer] Error: {e}")
    
    return state
