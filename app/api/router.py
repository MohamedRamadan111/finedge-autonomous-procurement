from fastapi import APIRouter, Depends, HTTPException
from app.models.a2a_protocol import ProcurementRequirement
from app.agents.graph import build_negotiation_graph
from app.agents.state import NegotiationState
from app.core.dependencies import get_checkpointer
from typing import Optional
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/v1")

class NegotiationRequest(BaseModel):
    requirement: ProcurementRequirement
    thread_id: Optional[str] = None

@router.post("/negotiate")
async def start_negotiation(req: NegotiationRequest, checkpointer = Depends(get_checkpointer)):
    
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    workflow = build_negotiation_graph()
    app_graph = workflow.compile(checkpointer=checkpointer)
    
    current_state = await app_graph.aget_state(config)
    
    if current_state and hasattr(current_state, "values") and current_state.values:
        initial_state = current_state.values
    else:
        initial_state = NegotiationState(
            requirement=req.requirement,
            current_offer=None,
            vendor_counter_offer=None,
            negotiation_history=[],
            iteration=0,
            is_approved_by_auditor=False,
            rejection_reason="",
            error_status=None,
            retry_count=0
        )
    
    final_state = await app_graph.ainvoke(initial_state, config=config)
    
    if final_state.get("error_status"):
        raise HTTPException(status_code=500, detail=final_state["error_status"])
        
    return {
        "status": "Success" if final_state.get("is_approved_by_auditor") else "Failed/Timeout",
        "thread_id": thread_id,
        "final_offer": final_state.get("vendor_counter_offer"),
        "rounds": final_state.get("iteration"),
        "history": final_state.get("negotiation_history"),
        "auditor_notes": final_state.get("rejection_reason")
    }

@router.get("/negotiate/{thread_id}")
async def get_negotiation_state(thread_id: str, checkpointer = Depends(get_checkpointer)):
    config = {"configurable": {"thread_id": thread_id}}
    workflow = build_negotiation_graph()
    app_graph = workflow.compile(checkpointer=checkpointer)
    state = await app_graph.aget_state(config)
    if not hasattr(state, "values") or not state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    return state.values
