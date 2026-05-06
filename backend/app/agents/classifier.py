from app.core.llm_client import UnifiedLLM
from app.models.state import AgentState
from app.core.config import settings


def classifier_agent(state: AgentState) -> AgentState:
    """Classify document type"""
    print(f"[Classifier] Analyzing document type...")

    if not state["extracted_text"]:
        state["errors"].append("No text to classify")
        return state

    try:
        llm = UnifiedLLM(temperature=0)
        
        # Take first 2000 chars for classification
        sample_text = state["extracted_text"][:2000]
        
        prompt = f"""Analyze this document and classify it into ONE of these categories:
- invoice
- contract
- letter
- chat
- receipt
- legal_document
- generic

Document text:
{sample_text}

Respond with ONLY the category name and confidence (0-1) in this format:
category: <category_name>
confidence: <0.XX>"""

        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse response
        lines = content.split("\n")
        category = None
        confidence = 0.0
        
        for line in lines:
            if line.startswith("category:"):
                category = line.split(":", 1)[1].strip()
            elif line.startswith("confidence:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except:
                    confidence = 0.5
        
        state["document_type"] = category or "generic"
        state["classification_confidence"] = confidence
        state["current_agent"] = "classifier"
        
        print(f"[Classifier] Type: {state['document_type']} (confidence: {confidence})")
        
    except Exception as e:
        state["errors"].append(f"Classification error: {str(e)}")
        state["document_type"] = "generic"
        state["classification_confidence"] = 0.0
        print(f"[Classifier] Error: {e}")
    
    return state
