from langchain_openai import ChatOpenAI
from app.agents.state import NegotiationState
from app.models.a2a_protocol import Offer
from app.prompts.negotiation import get_buyer_prompt, get_vendor_rejection_justification
from langsmith import traceable
from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_core.runnables import RunnableConfig

def get_llm(config: dict = None) -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o", temperature=0.1).with_structured_output(Offer)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
async def invoke_buyer_llm(prompt: str, config: RunnableConfig) -> Offer:
    llm = get_llm(config)
    return await llm.ainvoke(prompt, config=config)

@traceable(name="Buyer_Agent")
async def buyer_node(state: NegotiationState, config: RunnableConfig) -> dict:
    try:
        req = state["requirement"]
        history = "\n".join(state.get("negotiation_history", []))
        
        prompt = get_buyer_prompt(req.max_budget_per_unit, history)
        new_offer: Offer = await invoke_buyer_llm(prompt, config)
        
        history_list = state.get("negotiation_history", [])
        history_list.append(f"Buyer offered: {new_offer.price_per_unit}$")
        
        return {"current_offer": new_offer, "negotiation_history": history_list, "error_status": None}
    except Exception as e:
        return {"error_status": f"Buyer Node Error: {str(e)}"}

@traceable(name="Vendor_Agent")
async def vendor_node(state: NegotiationState, config: RunnableConfig) -> dict:
    try:
        buyer_offer = state.get("current_offer")
        if not buyer_offer:
            return {"error_status": "No buyer offer found for vendor"}
            
        req = state["requirement"]
        min_acceptable = req.max_budget_per_unit * 0.8
        
        counter = Offer(**buyer_offer.model_dump())
        
        if counter.price_per_unit >= min_acceptable:
            counter.justification = "Offer accepted."
        else:
            counter.price_per_unit = round(counter.price_per_unit * 1.10, 2)
            counter.justification = get_vendor_rejection_justification()

        history_list = state.get("negotiation_history", [])
        history_list.append(f"Vendor countered: {counter.price_per_unit}$")
        
        return {"vendor_counter_offer": counter, "negotiation_history": history_list, "error_status": None}
    except Exception as e:
         return {"error_status": f"Vendor Node Error: {str(e)}"}

@traceable(name="Auditor_Agent")
async def auditor_node(state: NegotiationState) -> dict:
    vendor_offer = state.get("vendor_counter_offer")
    req = state["requirement"]
    
    if not vendor_offer:
        return {"is_approved_by_auditor": False, "rejection_reason": "Missing vendor offer.", "error_status": None}
        
    if vendor_offer.price_per_unit > req.max_budget_per_unit:
        return {"is_approved_by_auditor": False, "rejection_reason": "Price exceeds budget.", "error_status": None}
        
    if "no return" in str(vendor_offer.penalties).lower():
         return {"is_approved_by_auditor": False, "rejection_reason": "Unacceptable penalty clause.", "error_status": None}

    return {"is_approved_by_auditor": True, "rejection_reason": "", "error_status": None}
