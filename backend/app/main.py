import shutil
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

# Copy working screenshot to docs/equityforge_demo.png
_brain_dir = Path("/home/Krishna-Singh/.gemini/antigravity-ide/brain/48a9146d-a4d3-4792-9be8-affbe0aae4b4")
_matches = sorted(_brain_dir.glob("media__*.png"))
if _matches:
    _docs_dir = Path(__file__).resolve().parent.parent.parent / "docs"
    _docs_dir.mkdir(exist_ok=True)
    shutil.copyfile(_matches[-1], _docs_dir / "equityforge_demo.png")

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

