from pydantic import BaseModel, Field
from typing import List, Optional

class Offer(BaseModel):
    """Standardized A2A communication protocol for procurement."""
    price_per_unit: float = Field(..., description="Proposed price per unit in USD")
    delivery_days: int = Field(..., description="Estimated delivery time in days")
    quality_compliance_score: float = Field(..., ge=0.0, le=1.0, description="1.0 means fully matches specs")
    penalties: List[str] = Field(default_factory=list, description="List of penalty clauses if any")
    justification: str = Field(..., description="Brief reasoning for this offer")

class ProcurementRequirement(BaseModel):
    product_name: str
    target_quantity: int
    max_budget_per_unit: float
    technical_specs: str
