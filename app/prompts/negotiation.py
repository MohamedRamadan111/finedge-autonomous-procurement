def get_buyer_prompt(max_budget: float, history: str) -> str:
    return f"""
    You are a strict B2B Buyer Agent. Target: {max_budget}$.
    History: {history}
    
    If the vendor's last offer is < {max_budget} and has no penalties, accept it by matching it.
    Otherwise, counter-offer with a lower price (e.g., 5% less than their offer).
    Output JSON ONLY based on the schema.
    """

def get_vendor_rejection_justification() -> str:
    return "Raw material costs are too high to accept your offer."
