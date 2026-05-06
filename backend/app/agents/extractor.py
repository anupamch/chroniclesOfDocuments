from app.models.state import AgentState
from app.core.config import settings

# Import production parser with fallbacks
from app.core.parsers_production import ProductionDocumentParser as DocumentParser


def extractor_agent(state: AgentState) -> AgentState:
    """Extract text and tables from document"""
    print(f"[Extractor] Processing: {state['file_name']}")
    print(f"[Extractor] OCR Method: {settings.ocr_method}")
    
    try:
        text, tables = DocumentParser.parse_document(state["file_path"])
        
        state["extracted_text"] = text
        state["tables"] = tables
        state["current_agent"] = "extractor"
        
        print(f"[Extractor] Extracted {len(text)} characters, {len(tables)} tables")
        
    except Exception as e:
        state["errors"].append(f"Extraction error: {str(e)}")
        print(f"[Extractor] Error: {e}")
    
    return state
