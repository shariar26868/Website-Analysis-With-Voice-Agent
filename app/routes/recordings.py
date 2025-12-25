"""
Call Recordings API Routes
"""
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import Optional
from app.config import get_db
from app.models import RecordingResponse
from app.services.storage_service import get_recording_url
from app.utils import logger

router = APIRouter()


@router.get("/{call_id}", response_model=RecordingResponse)
async def get_recording(call_id: str):
    """
    Get call recording and transcript
    
    Returns:
    - Recording URL (signed S3 URL or Twilio URL)
    - Transcript text
    - Call duration
    """
    try:
        db = get_db()
        
        # Find call log
        call_log = await db.call_logs.find_one({"_id": ObjectId(call_id)})
        
        if not call_log:
            raise HTTPException(status_code=404, detail="Call recording not found")
        
        # Get recording URL
        recording_url = None
        
        # Prefer S3 URL if available
        if call_log.get("recording_s3_url"):
            recording_url = await get_recording_url(call_log["recording_s3_url"])
        # Fallback to Twilio URL
        elif call_log.get("recording_url"):
            recording_url = call_log["recording_url"]
        
        return RecordingResponse(
            success=True,
            call_id=call_id,
            recording_url=recording_url,
            transcript=call_log.get("transcript"),
            duration=call_log.get("duration")
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to get recording: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcript/{call_id}")
async def get_transcript(call_id: str):
    """Get only the transcript for a call"""
    try:
        db = get_db()
        
        call_log = await db.call_logs.find_one(
            {"_id": ObjectId(call_id)},
            {"transcript": 1, "conversation_summary": 1, "key_points": 1}
        )
        
        if not call_log:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        return {
            "success": True,
            "call_id": call_id,
            "transcript": call_log.get("transcript"),
            "summary": call_log.get("conversation_summary"),
            "key_points": call_log.get("key_points", [])
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to get transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead/{lead_id}/recordings")
async def get_lead_recordings(lead_id: str):
    """Get all recordings for a specific lead"""
    try:
        db = get_db()
        
        # Verify lead exists
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get all call logs with recordings
        cursor = db.call_logs.find(
            {
                "lead_id": lead_id,
                "recording_url": {"$exists": True, "$ne": None}
            }
        ).sort("created_at", -1)
        
        recordings = await cursor.to_list(length=100)
        
        # Convert ObjectId and prepare response
        for recording in recordings:
            recording["_id"] = str(recording["_id"])
            
            # Get signed URL if S3
            if recording.get("recording_s3_url"):
                recording["playback_url"] = await get_recording_url(
                    recording["recording_s3_url"]
                )
            else:
                recording["playback_url"] = recording.get("recording_url")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "total": len(recordings),
            "recordings": recordings
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to get lead recordings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))