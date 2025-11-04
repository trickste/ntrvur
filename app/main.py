from fastapi import FastAPI
from app.routers.evaluate import router as evaluate_router

app = FastAPI(title="Agentic ATS & Interview Assistant (Local Ollama)")

app.include_router(evaluate_router)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
