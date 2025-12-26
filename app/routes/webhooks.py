# """
# Twilio Webhook Handlers
# """
# from fastapi import APIRouter, Request, Response
# from fastapi.responses import PlainTextResponse
# from twilio.twiml.voice_response import VoiceResponse
# from typing import Optional
# from app.services.sara_agent import handle_voice_input, start_conversation
# from app.utils import logger

# router = APIRouter()


# @router.post("/twilio/voice")
# async def twilio_voice_webhook(request: Request):
#     """
#     Handle incoming Twilio voice call
#     This is called when Sara initiates a call
#     """
#     try:
#         form_data = await request.form()
#         logger.info(f"Twilio voice webhook received: {dict(form_data)}")
        
#         call_sid = form_data.get("CallSid")
#         call_status = form_data.get("CallStatus")
        
#         # Start Sara conversation
#         twiml_response = await start_conversation(call_sid, form_data)
        
#         return Response(content=str(twiml_response), media_type="application/xml")
        
#     except Exception as e:
#         logger.error(f"Twilio voice webhook error: {str(e)}")
#         response = VoiceResponse()
#         response.say("Sorry, there was an error. Please try again later.")
#         return Response(content=str(response), media_type="application/xml")


# @router.post("/twilio/gather")
# async def twilio_gather_webhook(request: Request):
#     """
#     Handle user speech input during call
#     This is called when user speaks
#     """
#     try:
#         form_data = await request.form()
#         logger.info(f"Twilio gather webhook received")
        
#         call_sid = form_data.get("CallSid")
#         speech_result = form_data.get("SpeechResult", "")
        
#         # Process user input and get Sara's response
#         twiml_response = await handle_voice_input(call_sid, speech_result)
        
#         return Response(content=str(twiml_response), media_type="application/xml")
        
#     except Exception as e:
#         logger.error(f"Twilio gather webhook error: {str(e)}")
#         response = VoiceResponse()
#         response.say("Sorry, I didn't catch that. Could you please repeat?")
#         response.redirect("/api/v1/webhooks/twilio/gather")
#         return Response(content=str(response), media_type="application/xml")


# @router.post("/twilio/status")
# async def twilio_status_webhook(request: Request):
#     """
#     Handle call status updates
#     Called by Twilio when call status changes
#     """
#     try:
#         form_data = await request.form()
#         logger.info(f"Twilio status webhook: {dict(form_data)}")
        
#         call_sid = form_data.get("CallSid")
#         call_status = form_data.get("CallStatus")
#         call_duration = form_data.get("CallDuration")
        
#         # Update call log in database
#         from app.config import get_db
#         from datetime import datetime
        
#         db = get_db()
#         await db.call_logs.update_one(
#             {"call_sid": call_sid},
#             {
#                 "$set": {
#                     "status": call_status,
#                     "duration": int(call_duration) if call_duration else None,
#                     "ended_at": datetime.utcnow() if call_status == "completed" else None
#                 }
#             }
#         )
        
#         logger.info(f"Call {call_sid} status updated to: {call_status}")
        
#         return {"success": True}
        
#     except Exception as e:
#         logger.error(f"Twilio status webhook error: {str(e)}")
#         return {"success": False, "error": str(e)}


# @router.post("/twilio/recording")
# async def twilio_recording_webhook(request: Request):
#     """
#     Handle recording completion
#     Called by Twilio when recording is ready
#     """
#     try:
#         form_data = await request.form()
#         logger.info(f"Twilio recording webhook received")
        
#         call_sid = form_data.get("CallSid")
#         recording_url = form_data.get("RecordingUrl")
#         recording_sid = form_data.get("RecordingSid")
#         recording_duration = form_data.get("RecordingDuration")
        
#         # Save recording URL to database
#         from app.config import get_db
#         from app.services.storage_service import download_and_upload_recording
        
#         db = get_db()
        
#         # Download from Twilio and upload to S3 (optional)
#         s3_url = await download_and_upload_recording(recording_url, call_sid)
        
#         # Update call log
#         await db.call_logs.update_one(
#             {"call_sid": call_sid},
#             {
#                 "$set": {
#                     "recording_url": recording_url,
#                     "recording_s3_url": s3_url,
#                     "recording_sid": recording_sid,
#                     "duration": int(recording_duration) if recording_duration else None
#                 }
#             }
#         )
        
#         logger.info(f"Recording saved for call: {call_sid}")
        
#         return {"success": True}
        
#     except Exception as e:
#         logger.error(f"Twilio recording webhook error: {str(e)}")
#         return {"success": False, "error": str(e)}


# @router.get("/test")
# async def test_webhook():
#     """Test webhook endpoint"""
#     return {
#         "success": True,
#         "message": "Webhook endpoint is working"
#     }




#Final Update------------------


"""
Twilio Webhook Handlers
"""
from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse
from app.services.sara_agent import handle_voice_input, start_conversation
from app.utils import logger
from datetime import datetime

router = APIRouter()


@router.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    try:
        form_data = await request.form()
        logger.info(f"Twilio voice webhook received: {dict(form_data)}")

        call_sid = form_data.get("CallSid")
        twiml_response = await start_conversation(call_sid, form_data)

        return Response(content=str(twiml_response), media_type="application/xml")

    except Exception as e:
        logger.error(f"Twilio voice webhook error: {str(e)}")
        response = VoiceResponse()
        response.say("Sorry, there was an error. Please try again later.")
        return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/gather")
async def twilio_gather_webhook(request: Request):
    try:
        form_data = await request.form()
        logger.info("Twilio gather webhook received")

        call_sid = form_data.get("CallSid")
        speech_result = form_data.get("SpeechResult", "")

        twiml_response = await handle_voice_input(call_sid, speech_result)

        return Response(content=str(twiml_response), media_type="application/xml")

    except Exception as e:
        logger.error(f"Twilio gather webhook error: {str(e)}")
        response = VoiceResponse()
        response.say("Sorry, I didn't catch that. Please repeat.")
        response.redirect("/api/v1/webhooks/twilio/gather")
        return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/status")
async def twilio_status_webhook(request: Request):
    try:
        form_data = await request.form()
        logger.info(f"Twilio status webhook: {dict(form_data)}")

        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        call_duration = form_data.get("CallDuration")

        from app.config import get_db
        db = get_db()

        await db.call_logs.update_one(
            {"call_sid": call_sid},
            {
                "$set": {
                    "status": call_status,
                    "call_duration": int(call_duration) if call_duration else None,
                    "ended_at": datetime.utcnow() if call_status == "completed" else None
                }
            },
            upsert=True
        )

        logger.info(f"Call {call_sid} status updated to {call_status}")
        return {"success": True}

    except Exception as e:
        logger.error(f"Twilio status webhook error: {str(e)}")
        return {"success": False, "error": str(e)}


@router.post("/twilio/recording")
async def twilio_recording_webhook(request: Request):
    try:
        form_data = await request.form()
        logger.info("Twilio recording webhook received")

        call_sid = form_data.get("CallSid")
        recording_url = form_data.get("RecordingUrl")
        recording_sid = form_data.get("RecordingSid")
        recording_duration = form_data.get("RecordingDuration")

        from app.config import get_db
        from app.services.storage_service import download_and_upload_recording

        db = get_db()

        s3_url = await download_and_upload_recording(recording_url, call_sid)

        await db.call_logs.update_one(
            {"call_sid": call_sid},
            {
                "$set": {
                    "recording_url": recording_url,
                    "recording_s3_url": s3_url,
                    "recording_sid": recording_sid,
                    "recording_duration": int(recording_duration) if recording_duration else None
                }
            },
            upsert=True
        )

        logger.info(f"Recording saved for call {call_sid}")
        return {"success": True}

    except Exception as e:
        logger.error(f"Twilio recording webhook error: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/test")
async def test_webhook():
    return {
        "success": True,
        "message": "Twilio webhook endpoint working"
    }
