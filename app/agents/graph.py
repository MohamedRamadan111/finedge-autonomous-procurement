from langgraph.graph import StateGraph, END
from app.agents.state import NegotiationState
from app.agents.nodes import buyer_node, vendor_node, auditor_node
from app.core.config import settings

def should_continue(state: NegotiationState) -> str:
    """Conditional Edge logic."""
    if state.get("error_status"):
        return "end"
    if state.get("is_approved_by_auditor"):
        return "end"
    if state.get("iteration", 0) >= settings.max_negotiation_rounds:
        return "end"
    return "continue"

def build_negotiation_graph() -> StateGraph:
    workflow = StateGraph(NegotiationState)
    
    workflow.add_node("buyer", buyer_node)
    workflow.add_node("vendor", vendor_node)
    workflow.add_node("auditor", auditor_node)
    
    async def increment_iteration(state: NegotiationState):
        return {"iteration": state.get("iteration", 0) + 1}
    workflow.add_node("loop_manager", increment_iteration)

    workflow.set_entry_point("buyer")
    workflow.add_edge("buyer", "vendor")
    workflow.add_edge("vendor", "auditor")
    
    workflow.add_conditional_edges(
        "auditor",
        should_continue,
        {
            "end": END,
            "continue": "loop_manager"
        }
    )
    workflow.add_edge("loop_manager", "buyer")
    
    return workflow
