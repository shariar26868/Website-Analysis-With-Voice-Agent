"""
Sara AI Agent API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from bson import ObjectId
from datetime import datetime

from app.models import SaraCallRequest, SaraCallResponse, CallStatus
from app.config import get_db
from app.services.sara_agent import initiate_sara_call
from app.utils import logger

router = APIRouter()


@router.post("/call", response_model=SaraCallResponse)
async def request_sara_call(request: SaraCallRequest, background_tasks: BackgroundTasks):
    """
    Request Sara to call a lead
    
    Flow:
    1. Fetch lead data from database
    2. Initiate Twilio call
    3. Sara handles conversation with GPT-4
    4. Save call log
    """
    try:
        logger.info(f"Sara call requested for lead: {request.lead_id}")
        
        # Fetch lead from database
        db = get_db()
        lead = await db.leads.find_one({"_id": ObjectId(request.lead_id)})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get phone number
        phone_number = request.phone_number or lead.get("phone_number")
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        # Update lead status
        await db.leads.update_one(
            {"_id": ObjectId(request.lead_id)},
            {
                "$set": {
                    "call_status": CallStatus.IN_PROGRESS,
                    "last_call_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"call_attempts": 1}
            }
        )
        
        # Initiate call in background
        background_tasks.add_task(
            initiate_sara_call,
            lead_id=request.lead_id,
            lead_data=lead,
            phone_number=phone_number
        )
        
        logger.info(f"Sara call initiated for: {phone_number}")
        
        return SaraCallResponse(
            success=True,
            message="Sara will call shortly",
            call_id=request.lead_id,
            call_status=CallStatus.IN_PROGRESS
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to initiate Sara call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{lead_id}")
async def get_call_status(lead_id: str):
    """Get call status for a lead"""
    try:
        db = get_db()
        
        # Get lead
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get latest call log
        call_log = await db.call_logs.find_one(
            {"lead_id": lead_id},
            sort=[("created_at", -1)]
        )
        
        return {
            "success": True,
            "lead_id": lead_id,
            "call_status": lead.get("call_status"),
            "call_attempts": lead.get("call_attempts", 0),
            "last_call_date": lead.get("last_call_date"),
            "latest_call": call_log if call_log else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get call status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls/{lead_id}")
async def get_call_history(lead_id: str):
    """Get all call logs for a lead"""
    try:
        db = get_db()
        
        # Verify lead exists
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get all call logs
        cursor = db.call_logs.find({"lead_id": lead_id}).sort("created_at", -1)
        calls = await cursor.to_list(length=100)
        
        # Convert ObjectId to string
        for call in calls:
            call["_id"] = str(call["_id"])
        
        return {
            "success": True,
            "lead_id": lead_id,
            "total_calls": len(calls),
            "calls": calls
        }
        
    except Exception as e:
        logger.error(f"Failed to get call history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))