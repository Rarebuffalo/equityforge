from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.report_pipeline import generate_report

router = APIRouter(prefix="/api", tags=["reports"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "EquityForge API"}


@router.post("/generate-report")
async def generate_report_endpoint(
    company_name: str = Form(...),
    document: UploadFile = File(...),
):
    if not company_name.strip():
        raise HTTPException(status_code=400, detail="Company name is required.")

    filename = document.filename or "upload.pdf"
    content = await document.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        pdf_bytes, report = generate_report(company_name.strip(), content, filename)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {exc}",
        ) from exc

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in company_name.strip())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}_research_report.pdf"',
            "X-Report-Company": report.company_name,
            "X-Report-Rating": report.rating or "N/A",
        },
    )
