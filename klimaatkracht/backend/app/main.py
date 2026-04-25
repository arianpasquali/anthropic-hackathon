"""FastAPI app entry point.

Routes are mounted under `/api/*`. Auth is mocked for the hackathon — every
request is treated as the demo buyer or chapter coordinator depending on
which dashboard called it.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chapters, fund, methodology, operations, reports

app = FastAPI(title="Klimaatkracht API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(operations.router)
app.include_router(chapters.router)
app.include_router(fund.router)
app.include_router(reports.router)
app.include_router(methodology.router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
