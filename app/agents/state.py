from typing import TypedDict, List, Optional
from app.models.a2a_protocol import Offer, ProcurementRequirement

class NegotiationState(TypedDict):
    """Represents the shared memory (State) during the LangGraph execution."""
    requirement: ProcurementRequirement
    current_offer: Optional[Offer]
    vendor_counter_offer: Optional[Offer]
    negotiation_history: List[str]
    iteration: int
    is_approved_by_auditor: bool
    rejection_reason: str
    error_status: Optional[str]
    retry_count: int
