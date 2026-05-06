"""
Legal Advice API Routes

Provides endpoints for:
- POST /api/legal/advise - Get legal advice
- GET /api/legal/categories - List legal categories
- GET /api/legal/search - Search laws
- POST /api/legal/export - Export legal advice as PDF/DOC
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
from app.legal.models import (
    LegalAdviceRequest,
    LegalAdviceResponse,
    SearchRequest,
    SearchResponse,
)
from app.legal.query_handler import legal_query_handler
from app.legal.categorizer import legal_categorizer
from app.legal.api_client import legal_api_client
from app.api.dependencies import get_current_user_flexible
from app.legal.document_generator import generate_legal_document

router = APIRouter(prefix="/legal", tags=["legal"])


@router.post("/advise", response_model=LegalAdviceResponse)
async def get_legal_advice(
    request: LegalAdviceRequest,
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Get legal advice based on user's query.

    This endpoint:
    1. Categorizes the legal issue
    2. Searches for relevant provisions via legal APIs
    3. Searches for relevant case laws
    4. Generates structured legal advice
    """
    return await legal_query_handler.process_legal_query(request)


@router.get("/categories")
async def get_legal_categories(
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Get all available legal categories.

    Returns a list of legal categories for Indian law including:
    - Criminal Law
    - Civil Dispute
    - Property Dispute
    - Family Dispute
    - Labor & Employment
    - Corporate & Commercial
    - Tax Law
    - Consumer Protection
    - Constitutional Law
    - Data Privacy & IT
    - RTI
    - Motor Accident
    """
    return {
        "categories": legal_categorizer.get_all_categories()
    }


@router.get("/categories/{category_id}")
async def get_category_details(
    category_id: str,
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Get details for a specific legal category.
    """
    category = legal_categorizer.get_category_info(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/search", response_model=SearchResponse)
async def search_laws(
    q: str = Query(..., description="Search query/keywords"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Search for legal provisions and case laws.

    Searches across integrated legal APIs:
    - Indian Kanoon (case law)
    - InsightLaw API (legal research)
    - Kleopatra API (court data)
    - eCourts API (case dataset)
    """
    # Search provisions
    provisions, prov_sources = await legal_api_client.search_provisions(
        query=q,
        category=category,
        limit=limit
    )

    # Search cases
    cases, case_sources = await legal_api_client.search_cases(
        query=q,
        category=category,
        limit=limit
    )

    return SearchResponse(
        provisions=[
            {
                "act": p.act,
                "section": p.section,
                "title": p.title,
                "description": p.description[:200],
                "score": 1.0,
                "source": p.source
            }
            for p in provisions
        ],
        cases=[
            {
                "case_name": c.case_name,
                "year": c.year,
                "court": c.court,
                "summary": c.summary[:200] if c.summary else None,
                "score": 1.0,
                "source": c.source
            }
            for c in cases
        ],
        total_results=len(provisions) + len(cases),
        sources_used=list(set(prov_sources + case_sources))
    )


@router.get("/health")
async def legal_health_check():
    """
    Health check for legal advice service.
    """
    return {
        "status": "healthy",
        "service": "Legal Advice API",
        "providers": {
            "indian_kanoon": True,  # Web-based, always available
            "insightlaw": bool(legal_api_client.providers),
            "kleopatra": "kleopatra" in legal_api_client.providers,
            "ecourts": "ecourts" in legal_api_client.providers
        }
    }


@router.post("/export")
async def export_legal_advice(
    advice_data: dict,
    format: str = Query("pdf", description="Export format: pdf or doc"),
    case_number: Optional[str] = Query(None, description="Case number for filename"),
    case_title: Optional[str] = Query(None, description="Case title for document"),
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    Export legal advice as PDF or DOC document.

    Generates a downloadable document from legal advice data with:
    - Structured layout with headings
    - All relevant legal provisions and case laws
    - Professional formatting
    - Disclaimer
    """
    try:
        file_path = generate_legal_document(
            advice_data=advice_data,
            format=format,
            case_number=case_number,
            case_title=case_title
        )

        # Determine filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"legal_advice_{case_number or 'case'}_{timestamp}.{format}"

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate document: {str(e)}")
