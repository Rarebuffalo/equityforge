from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="EquityForge API",
    description="Transform Financial Documents into Institutional-Quality Equity Research Reports with AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "name": "EquityForge",
        "tagline": "Transform Financial Documents into Institutional-Quality Equity Research Reports with AI.",
        "docs": "/docs",
    }
