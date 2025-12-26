# """
# Call Recordings API Routes
# """
# from fastapi import APIRouter, HTTPException
# from bson import ObjectId
# from typing import Optional
# from app.config import get_db
# from app.models import RecordingResponse
# from app.services.storage_service import get_recording_url
# from app.utils import logger

# router = APIRouter()


# @router.get("/{call_id}", response_model=RecordingResponse)
# async def get_recording(call_id: str):
#     """
#     Get call recording and transcript
    
#     Returns:
#     - Recording URL (signed S3 URL or Twilio URL)
#     - Transcript text
#     - Call duration
#     """
#     try:
#         db = get_db()
        
#         # Find call log
#         call_log = await db.call_logs.find_one({"_id": ObjectId(call_id)})
        
#         if not call_log:
#             raise HTTPException(status_code=404, detail="Call recording not found")
        
#         # Get recording URL
#         recording_url = None
        
#         # Prefer S3 URL if available
#         if call_log.get("recording_s3_url"):
#             recording_url = await get_recording_url(call_log["recording_s3_url"])
#         # Fallback to Twilio URL
#         elif call_log.get("recording_url"):
#             recording_url = call_log["recording_url"]
        
#         return RecordingResponse(
#             success=True,
#             call_id=call_id,
#             recording_url=recording_url,
#             transcript=call_log.get("transcript"),
#             duration=call_log.get("duration")
#         )
        
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Failed to get recording: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/transcript/{call_id}")
# async def get_transcript(call_id: str):
#     """Get only the transcript for a call"""
#     try:
#         db = get_db()
        
#         call_log = await db.call_logs.find_one(
#             {"_id": ObjectId(call_id)},
#             {"transcript": 1, "conversation_summary": 1, "key_points": 1}
#         )
        
#         if not call_log:
#             raise HTTPException(status_code=404, detail="Transcript not found")
        
#         return {
#             "success": True,
#             "call_id": call_id,
#             "transcript": call_log.get("transcript"),
#             "summary": call_log.get("conversation_summary"),
#             "key_points": call_log.get("key_points", [])
#         }
        
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Failed to get transcript: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/lead/{lead_id}/recordings")
# async def get_lead_recordings(lead_id: str):
#     """Get all recordings for a specific lead"""
#     try:
#         db = get_db()
        
#         # Verify lead exists
#         lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
#         if not lead:
#             raise HTTPException(status_code=404, detail="Lead not found")
        
#         # Get all call logs with recordings
#         cursor = db.call_logs.find(
#             {
#                 "lead_id": lead_id,
#                 "recording_url": {"$exists": True, "$ne": None}
#             }
#         ).sort("created_at", -1)
        
#         recordings = await cursor.to_list(length=100)
        
#         # Convert ObjectId and prepare response
#         for recording in recordings:
#             recording["_id"] = str(recording["_id"])
            
#             # Get signed URL if S3
#             if recording.get("recording_s3_url"):
#                 recording["playback_url"] = await get_recording_url(
#                     recording["recording_s3_url"]
#                 )
#             else:
#                 recording["playback_url"] = recording.get("recording_url")
        
#         return {
#             "success": True,
#             "lead_id": lead_id,
#             "total": len(recordings),
#             "recordings": recordings
#         }
        
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Failed to get lead recordings: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))







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


@router.get("/{call_log_id}", response_model=RecordingResponse)
async def get_recording(call_log_id: str):
    """
    Get call recording and transcript by call_log_id
    
    Args:
        call_log_id: MongoDB ObjectId of the call_log document
    
    Returns:
        Recording URL (signed S3 URL or Twilio URL), transcript, duration
    """
    try:
        logger.info(f"Fetching recording for call_log_id: {call_log_id}")
        
        if not ObjectId.is_valid(call_log_id):
            raise HTTPException(status_code=400, detail="Invalid call_log_id format")
        
        db = get_db()
        
        # Find call log by _id
        call_log = await db.call_logs.find_one({"_id": ObjectId(call_log_id)})
        
        if not call_log:
            logger.warning(f"Call log not found: {call_log_id}")
            raise HTTPException(status_code=404, detail="Call recording not found")
        
        # Get recording URL
        recording_url = None
        
        # Prefer S3 URL if available
        if call_log.get("recording_s3_url"):
            logger.info(f"Generating signed URL for S3: {call_log['recording_s3_url']}")
            recording_url = await get_recording_url(call_log["recording_s3_url"])
        # Fallback to Twilio URL
        elif call_log.get("recording_url"):
            logger.info(f"Using Twilio URL")
            recording_url = call_log["recording_url"]
        
        return RecordingResponse(
            success=True,
            call_id=call_log_id,
            recording_url=recording_url,
            transcript=call_log.get("transcript"),
            duration=call_log.get("duration")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recording: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcript/{call_log_id}")
async def get_transcript(call_log_id: str):
    """Get only the transcript for a call"""
    try:
        if not ObjectId.is_valid(call_log_id):
            raise HTTPException(status_code=400, detail="Invalid call_log_id format")
        
        db = get_db()
        
        call_log = await db.call_logs.find_one(
            {"_id": ObjectId(call_log_id)},
            {"transcript": 1, "conversation_summary": 1, "key_points": 1}
        )
        
        if not call_log:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        return {
            "success": True,
            "call_log_id": call_log_id,
            "transcript": call_log.get("transcript"),
            "summary": call_log.get("conversation_summary"),
            "key_points": call_log.get("key_points", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead/{lead_id}/recordings")
async def get_lead_recordings(lead_id: str):
    """
    Get all recordings for a specific lead
    
    Use this when you have lead_id instead of call_log_id
    """
    try:
        if not ObjectId.is_valid(lead_id):
            raise HTTPException(status_code=400, detail="Invalid lead_id format")
        
        db = get_db()
        
        # Verify lead exists
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get all call logs with recordings
        cursor = db.call_logs.find(
            {
                "lead_id": lead_id,
                "$or": [
                    {"recording_url": {"$exists": True, "$ne": None}},
                    {"recording_s3_url": {"$exists": True, "$ne": None}}
                ]
            }
        ).sort("created_at", -1)
        
        recordings = await cursor.to_list(length=100)
        
        # Convert ObjectId and prepare response
        result = []
        for recording in recordings:
            call_log_id = str(recording["_id"])
            
            # Get signed URL if S3
            playback_url = None
            if recording.get("recording_s3_url"):
                playback_url = await get_recording_url(recording["recording_s3_url"])
            elif recording.get("recording_url"):
                playback_url = recording["recording_url"]
            
            result.append({
                "call_log_id": call_log_id,
                "call_sid": recording.get("call_sid"),
                "playback_url": playback_url,
                "duration": recording.get("duration"),
                "transcript": recording.get("transcript"),
                "status": recording.get("status"),
                "outcome": recording.get("outcome"),
                "created_at": recording.get("created_at")
            })
        
        return {
            "success": True,
            "lead_id": lead_id,
            "business_name": lead.get("business_name"),
            "total": len(result),
            "recordings": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lead recordings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead/{lead_id}/latest")
async def get_latest_recording(lead_id: str):
    """
    Get the latest recording for a lead (shortcut endpoint)
    
    Returns the most recent recording with signed URL
    """
    try:
        if not ObjectId.is_valid(lead_id):
            raise HTTPException(status_code=400, detail="Invalid lead_id format")
        
        db = get_db()
        
        # Get latest call log with recording
        call_log = await db.call_logs.find_one(
            {
                "lead_id": lead_id,
                "$or": [
                    {"recording_url": {"$exists": True, "$ne": None}},
                    {"recording_s3_url": {"$exists": True, "$ne": None}}
                ]
            },
            sort=[("created_at", -1)]
        )
        
        if not call_log:
            raise HTTPException(status_code=404, detail="No recording found for this lead")
        
        # Get recording URL
        recording_url = None
        if call_log.get("recording_s3_url"):
            recording_url = await get_recording_url(call_log["recording_s3_url"])
        elif call_log.get("recording_url"):
            recording_url = call_log["recording_url"]
        
        return {
            "success": True,
            "call_log_id": str(call_log["_id"]),
            "lead_id": lead_id,
            "recording_url": recording_url,
            "transcript": call_log.get("transcript"),
            "duration": call_log.get("duration"),
            "call_sid": call_log.get("call_sid"),
            "status": call_log.get("status"),
            "outcome": call_log.get("outcome"),
            "created_at": call_log.get("created_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest recording: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))