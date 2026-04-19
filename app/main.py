from fastapi import FastAPI
from app.api.router import router

app = FastAPI(title="FinEdge Multi-Agent Procurement Hub", version="2.0.0")
app.include_router(router)
