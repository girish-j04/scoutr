"""FastAPI router for POST /export. Dev 1 can include this in the main app.

Usage:
    from scoutr.api.export_router import export_router
    app.include_router(export_router, tags=["export"])
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from scoutr.export.pdf_service import generate_pdf

export_router = APIRouter(prefix="", tags=["export"])


class ExportRequest(BaseModel):
    """Request body for POST /export."""

    player_ids: list[int]
    query: str = ""
    club: str = "Leeds United"


@export_router.post("/export")
async def export_report(req: ExportRequest) -> Response:
    """Generate and return PDF scouting report. Uses golden path fallback if API fails."""
    try:
        pdf_bytes = generate_pdf(
            player_ids=req.player_ids,
            query=req.query,
            club=req.club,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=scoutr_report.pdf"},
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")
