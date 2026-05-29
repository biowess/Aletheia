from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.core.database import get_db
from app.services.report_version_service import ReportVersionService
from app.services.case_service import CaseService
from app.services.follow_up_service import FollowUpService
from app.export.pdf_service import PDFExportService
from app.export.pptx_service import PPTXExportService

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/reports/{report_id}/pdf")
async def export_report_pdf(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and download a PDF export for a specific report version.
    """
    # Fetch ReportVersion by ID
    report = await ReportVersionService.get_report_version(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Fetch the associated Case
    case = await CaseService.get_case(db, report.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Associated case not found")
        
    # Fetch all FollowUpEntry records for the case
    follow_ups = await FollowUpService.list_follow_ups_for_case(db, report.case_id)
    
    # Generate PDF synchronously
    try:
        pdf_service = PDFExportService()
        pdf_path = pdf_service.generate_report_pdf(report, case, follow_ups)
    except Exception as e:
        raise HTTPException(status_code=500, detail="PDF generation failed")
        
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF generation failed")
        
    filename = f"clinical_report_v{report.version_number}.pdf"
    
    # Return the file as a downloadable response
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/reports/{report_id}/pptx")
async def export_report_pptx(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and download a PowerPoint export for a specific report version.
    """
    report = await ReportVersionService.get_report_version(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = await CaseService.get_case(db, report.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Associated case not found")

    follow_ups = await FollowUpService.list_follow_ups_for_case(db, report.case_id)

    try:
        pptx_service = PPTXExportService()
        pptx_path = pptx_service.generate_report_pptx(report, case, follow_ups)
    except Exception as e:
        raise HTTPException(status_code=500, detail="PPTX generation failed")

    if not os.path.exists(pptx_path):
        raise HTTPException(status_code=500, detail="PPTX generation failed")

    filename = f"clinical_report_v{report.version_number}.pptx"
    return FileResponse(
        path=pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename
    )
