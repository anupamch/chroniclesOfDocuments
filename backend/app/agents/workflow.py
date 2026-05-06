from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.agents.extractor import extractor_agent
from app.agents.classifier import classifier_agent
from app.agents.analyzer import analyzer_agent
from app.agents.synthesizer import synthesizer_agent


def create_workflow():
    """Create the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extractor", extractor_agent)
    workflow.add_node("classifier", classifier_agent)
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    
    # Define edges (linear flow)
    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "classifier")
    workflow.add_edge("classifier", "analyzer")
    workflow.add_edge("analyzer", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()
