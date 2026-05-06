from datetime import datetime
from typing import List, Dict
from app.services.mongodb import mongodb
from app.services.case_service import CaseService
from app.services.document_service import DocumentService
from app.agents.workflow import create_workflow
from app.models.state import AgentState
from app.services.websocket_manager import manager


class ScanService:
    
    @staticmethod
    async def start_scan(case_id: str) -> dict:
        """Start scanning all documents in a case"""
        
        # Validate case exists
        case = await CaseService.get_case(case_id)
        
        # Get all documents
        documents = await DocumentService.get_case_documents(case_id)
        
        if not documents:
            raise ValueError(f"No documents found for case '{case_id}'")
        
        # Filter pending documents
        pending_docs = [doc for doc in documents if doc["status"] == "pending"]
        
        # If no pending docs, we assume a rescan is requested and reset all docs to pending
        if not pending_docs:
            print(f"Rescan requested for case {case_id}. Resetting {len(documents)} documents to pending.")
            for doc in documents:
                await DocumentService.update_document_status(doc["document_id"], "pending")
            pending_docs = documents
        
        return {
            "case_id": case_id,
            "case_number": case["case_number"],
            "total_documents": len(pending_docs),
            "status": "started",
            "message": f"Scan started for {len(pending_docs)} documents"
        }

    @staticmethod
    async def update_case_analysis_status(case_id: str, status: str):
        """Update the analysis status on the case"""
        db = mongodb.get_db()
        if db is not None:
            await db.cases.update_one(
                {"case_id": case_id},
                {"$set": {"analysis_status": status}}
            )
    
    @staticmethod
    async def process_case_documents(case_id: str) -> dict:
        """Process all documents in a case using agent workflow"""

        # Get case and documents
        case = await CaseService.get_case(case_id)
        documents = await DocumentService.get_case_documents(case_id)

        pending_docs = [doc for doc in documents if doc["status"] == "pending"]

        if not pending_docs:
            return {
                "case_id": case_id,
                "status": "completed",
                "message": "No pending documents to process"
            }

        # Set analysis status to in_progress
        await ScanService.update_case_analysis_status(case_id, "in_progress")

        # Create workflow
        workflow = create_workflow()
        
        # Process each document
        all_results = []
        all_timeline_events = []
        
        db = mongodb.get_db()
        
        for doc in pending_docs:
            print(f"\n{'='*60}")
            print(f"Processing: {doc['file_name']}")
            print(f"{'='*60}\n")
            
            # Update status to processing
            await DocumentService.update_document_status(doc["document_id"], "processing")
            
            # Initialize agent state
            initial_state: AgentState = {
                "document_id": doc["document_id"],
                "file_path": doc["file_path"],
                "file_name": doc["file_name"],
                "file_type": doc["file_type"],
                "extracted_text": "",
                "tables": [],
                "document_type": None,
                "classification_confidence": None,
                "analysis_results": {},
                "summary": "",
                "timeline_events": [],
                "errors": [],
                "current_agent": ""
            }
            
            try:
                # Run workflow in a separate thread to avoid blocking the event loop
                import asyncio
                final_state = await asyncio.to_thread(workflow.invoke, initial_state)
                
                # Save analysis results
                analysis_result = {
                    "document_id": doc["document_id"],
                    "case_id": case_id,
                    "file_name": doc["file_name"],
                    "document_type": final_state["document_type"],
                    "confidence": final_state["classification_confidence"],
                    "summary": final_state["summary"],
                    "timeline_events": final_state["timeline_events"],
                    "analysis_results": final_state["analysis_results"],
                    "errors": final_state["errors"],
                    "processed_at": datetime.utcnow()
                }
                
                if db is not None:
                    # Delete existing analysis results for this document if they exist
                    await db.analysis_results.delete_many({"document_id": doc["document_id"]})
                    await db.analysis_results.insert_one(analysis_result)
                
                all_results.append(analysis_result)
                
                # Collect timeline events
                for event in final_state["timeline_events"]:
                    all_timeline_events.append({
                        **event,
                        "source": doc["file_name"]
                    })
                
                # Update document status to completed
                await DocumentService.update_document_status(doc["document_id"], "completed")

                print(f"\n✓ Completed: {doc['file_name']}")
                
                # Notify via WebSocket
                await manager.broadcast({
                    "type": "document_processed",
                    "case_id": case_id,
                    "document_id": doc["document_id"],
                    "file_name": doc["file_name"]
                })
                
                # Give the event loop a small break between documents
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"\n✗ Failed: {doc['file_name']}")
                print(f"  Error: {e}")
                
                # Update document status to failed
                await DocumentService.update_document_status(
                    doc["document_id"], 
                    "failed", 
                    str(e)
                )
        
        # Generate timeline story
        timeline_story = ScanService.generate_timeline_story(
            case["case_number"],
            all_results,
            all_timeline_events
        )
        
        # Save timeline story to case
        if db is not None:
            await db.cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "timeline_story": timeline_story,
                        "last_scan_at": datetime.utcnow()
                    }
                }
            )
        
        # Notify scan complete via WebSocket
        await manager.broadcast({
            "type": "scan_complete",
            "case_id": case_id,
            "message": "AI Analysis complete"
        })

        # Update case analysis status to completed
        await ScanService.update_case_analysis_status(case_id, "completed")

        return {
            "case_id": case_id,
            "status": "completed",
            "total_documents": len(pending_docs),
            "results": all_results,
            "timeline_story": timeline_story
        }
    
    @staticmethod
    def generate_timeline_story(case_number: str, results: List[dict], timeline_events: List[dict]) -> str:
        """Generate a narrative timeline story"""
        
        story = f"TIMELINE STORY - Case: {case_number}\n"
        story += "=" * 60 + "\n\n"
        
        # Document summary
        story += f"Analyzed {len(results)} documents:\n"
        for result in results:
            story += f"  • {result['file_name']} ({result['document_type']})\n"
        story += "\n"
        
        # Sort timeline events by date
        sorted_events = sorted(
            [e for e in timeline_events if e.get("date") != "unknown"],
            key=lambda x: x.get("date", "")
        )
        unknown_events = [e for e in timeline_events if e.get("date") == "unknown"]
        
        # Timeline events
        if sorted_events:
            story += "CHRONOLOGICAL TIMELINE:\n"
            story += "-" * 60 + "\n\n"
            
            for event in sorted_events:
                story += f"📅 {event['date']}\n"
                story += f"   {event['event']}\n"
                story += f"   Source: {event['source']}\n\n"
        
        # Events without dates
        if unknown_events:
            story += "\nEVENTS (Date Unknown):\n"
            story += "-" * 60 + "\n\n"
            
            for event in unknown_events:
                story += f"   • {event['event']}\n"
                story += f"     Source: {event['source']}\n\n"
        
        # Document summaries
        story += "\nDOCUMENT SUMMARIES:\n"
        story += "-" * 60 + "\n\n"
        
        for result in results:
            story += f"{result['file_name']}:\n"
            story += f"{result['summary']}\n\n"
        
        return story
    
    @staticmethod
    async def get_scan_status(case_id: str) -> dict:
        """Get scan status for a case"""
        
        case = await CaseService.get_case(case_id)
        documents = await DocumentService.get_case_documents(case_id)
        
        db = mongodb.get_db()
        
        # Get analysis results
        results = []
        if db is not None:
            cursor = db.analysis_results.find({"case_id": case_id})
            results = await cursor.to_list(length=None)
        
        # Count statuses
        total_docs = len(documents)
        processed_docs = len([d for d in documents if d["status"] == "completed"])
        failed_docs = len([d for d in documents if d["status"] == "failed"])
        pending_docs = len([d for d in documents if d["status"] == "pending"])
        
        # Determine overall status
        if pending_docs == total_docs:
            status = "not_started"
        elif pending_docs > 0:
            status = "in_progress"
        else:
            status = "completed"
        
        return {
            "case_id": case_id,
            "case_number": case["case_number"],
            "status": status,
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "failed_documents": failed_docs,
            "pending_documents": pending_docs,
            "results": results,
            "timeline_story": case.get("timeline_story")
        }
