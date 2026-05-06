from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from pathlib import Path
from datetime import datetime

from app.models.schemas import (
    CreateCaseRequest, CreateCaseResponse,
    UploadFilesResponse, StartScanRequest, StartScanResponse,
    ScanStatusResponse, CaseListResponse, CaseDetailResponse,
    CaseDocumentsResponse, CaseStatus
)
from app.services.case_service import CaseService
from app.services.document_service import DocumentService
from app.services.scan_service import ScanService
from app.services.websocket_manager import manager
from app.api.dependencies import get_current_user, get_current_user_flexible

router = APIRouter()


@router.post("/cases", response_model=CreateCaseResponse, status_code=201)
async def create_case(request: CreateCaseRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new case and its folder
    """
    try:
        case = await CaseService.create_case(
            case_number=request.case_number,
            title=request.title,
            description=request.description,
            user_id=current_user["user_id"]
        )
        
        return CreateCaseResponse(
            case_id=case["case_id"],
            case_number=case["case_number"],
            title=case["title"],
            folder_path=case["folder_path"],
            created_at=case["created_at"],
            status=case["status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create case: {str(e)}")


@router.post("/cases/{case_id}/documents", response_model=UploadFilesResponse)
async def upload_documents(
    case_id: str,
    files: List[UploadFile] = File(..., description="Documents to upload"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple documents to a case
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        result = await DocumentService.upload_documents(case_id, files, current_user["user_id"])
        return UploadFilesResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/cases/{case_id}/scan", response_model=StartScanResponse)
async def start_scan(case_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Start scanning and analyzing all documents in a case
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")

        # Set analysis status to started
        await ScanService.update_case_analysis_status(case_id, "in_progress")

        # Start scan
        result = await ScanService.start_scan(case_id)
        
        # Process documents in background
        background_tasks.add_task(ScanService.process_case_documents, case_id)
        
        return StartScanResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/cases/{case_id}/scan/status", response_model=ScanStatusResponse)
async def get_scan_status(case_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get scan status and results for a case
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        result = await ScanService.get_scan_status(case_id)
        return ScanStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/cases", response_model=CaseListResponse)
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    current_user: dict = Depends(get_current_user)
):
    """
    List all cases with pagination, search, and sorting
    """
    try:
        result = await CaseService.list_cases(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            sort_by=sort_by or "created_at",
            sort_order=sort_order or "desc",
            user_id=current_user["user_id"],
            is_admin=current_user.get("role") == "admin"
        )
        return CaseListResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cases: {str(e)}")


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
async def get_case_details(case_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get detailed information about a case
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        result = await CaseService.get_case_with_documents(case_id)
        case = result["case"]

        return CaseDetailResponse(
            case_id=case.get("case_id"),
            case_number=case.get("case_number"),
            title=case.get("title"),
            description=case.get("description"),
            status=case.get("status"),
            folder_path=case.get("folder_path"),
            created_at=case.get("created_at"),
            updated_at=case.get("updated_at"),
            total_documents=result["total_documents"],
            timeline_story=case.get("timeline_story"),
            last_scan_at=case.get("last_scan_at"),
            analysis_status=case.get("analysis_status")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get case details: {str(e)}")


@router.get("/cases/{case_id}/documents", response_model=CaseDocumentsResponse)
async def get_case_documents(case_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get all documents for a case
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        result = await CaseService.get_case_with_documents(case_id)
        return CaseDocumentsResponse(
            case_id=case_id,
            documents=result["documents"],
            total=result["total_documents"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")


@router.get("/cases/{case_id}/documents/{document_id}/view")
async def view_document(
    case_id: str, 
    document_id: str, 
    download: bool = Query(False),
    current_user: dict = Depends(get_current_user_flexible)
):
    """
    View/Download an uploaded document
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        # Get document metadata
        doc = await DocumentService.get_document(case_id, document_id)
        
        # Ownership check: must be owner or admin
        is_admin = current_user.get("role") == "admin"
        if not is_admin and doc.get("created_by") and doc.get("created_by") != current_user["user_id"]:
            raise HTTPException(status_code=401, detail="Not authorized to access this document")
        
        file_path = doc.get("file_path")
        if not file_path or not os.path.exists(file_path):
            case = await CaseService.get_case(case_id)
            case_folder = Path(case["folder_path"])
            file_ext = os.path.splitext(doc["file_name"])[1].lower()
            file_path = case_folder / f"{document_id}{file_ext}"
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Physical file not found on server")

        headers = {}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="{doc["file_name"]}"'

        return FileResponse(
            path=file_path,
            filename=doc["file_name"],
            media_type=doc.get("file_type", "application/octet-stream"),
            headers=headers
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to view document: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Chronicles of Documents API"
    }


@router.delete("/cases/{case_id}")
async def delete_case_endpoint(case_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a case
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        deleted_count = await DocumentService.delete_all_documents(case_id)
        await CaseService.delete_case(case_id)
        return {"status": "success", "message": f"Case deleted successfully. {deleted_count} documents removed."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete case: {str(e)}")


@router.delete("/cases/{case_id}/documents/{document_id}")
async def delete_document_endpoint(case_id: str, document_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a document
    """
    try:
        # Verify access
        await CaseService.get_case(case_id, current_user["user_id"], current_user.get("role") == "admin")
        
        # Get document metadata
        doc = await DocumentService.get_document(case_id, document_id)
        
        # Ownership check: must be owner or admin
        is_admin = current_user.get("role") == "admin"
        if not is_admin and doc.get("created_by") and doc.get("created_by") != current_user["user_id"]:
            raise HTTPException(status_code=401, detail="Not authorized to delete this document")
            
        await DocumentService.delete_document(case_id, document_id)
        return {"status": "success", "message": "Document deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    print(f"[WS] New connection attempt: {client_id}")
    await manager.connect(client_id, websocket)
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_json({"type": "keepalive"})
    except WebSocketDisconnect:
        manager.disconnect(client_id, websocket)
    except Exception as e:
        print(f"[WS] Error with {client_id}: {e}")
        manager.disconnect(client_id, websocket)
