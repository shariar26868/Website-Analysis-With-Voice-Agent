"""
Twilio Service - Call Handling
"""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import httpx
from typing import Dict, Any, Optional

from app.config import settings
from app.utils import logger

# Initialize Twilio client
twilio_client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN
)


async def make_call(
    to_number: str,
    webhook_url: str,
    status_callback_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiate an outbound call via Twilio
    
    Args:
        to_number: Phone number to call
        webhook_url: URL for voice webhook
        status_callback_url: URL for status updates
    
    Returns:
        Call details (SID, status, etc.)
    """
    try:
        logger.info(f"Initiating call to: {to_number}")
        
        call = twilio_client.calls.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=webhook_url,
            status_callback=status_callback_url,
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            record=True,  # Enable call recording
            recording_status_callback=webhook_url.replace('/voice', '/recording')
        )
        
        logger.info(f"Call initiated: {call.sid}")
        
        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
            "to": call.to,
            "from": call.from_
        }
        
    except Exception as e:
        logger.error(f"Failed to make call: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def create_voice_response(message: str, gather_input: bool = True) -> VoiceResponse:
    """
    Create TwiML voice response
    
    Args:
        message: Text Sara should say
        gather_input: Whether to listen for user response
    
    Returns:
        TwiML VoiceResponse object
    """
    response = VoiceResponse()
    
    if gather_input:
        # Gather user speech input
        gather = Gather(
            input='speech',
            action='/api/v1/webhooks/twilio/gather',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        gather.say(message, voice='Polly.Joanna')
        response.append(gather)
        
        # Fallback if no input
        response.say("I didn't hear anything. Please call us back when you're ready.")
        
    else:
        # Just say and hang up
        response.say(message, voice='Polly.Joanna')
        response.hangup()
    
    return response


async def get_call_status(call_sid: str) -> Dict[str, Any]:
    """
    Get current status of a call
    
    Returns:
        Call status, duration, etc.
    """
    try:
        call = twilio_client.calls(call_sid).fetch()
        
        return {
            "call_sid": call.sid,
            "status": call.status,
            "duration": call.duration,
            "start_time": call.start_time,
            "end_time": call.end_time,
            "direction": call.direction
        }
        
    except Exception as e:
        logger.error(f"Failed to get call status: {str(e)}")
        return {
            "error": str(e)
        }


async def download_recording(recording_url: str) -> bytes:
    """
    Download call recording from Twilio
    
    Args:
        recording_url: Twilio recording URL
    
    Returns:
        Recording audio bytes
    """
    try:
        logger.info(f"Downloading recording from Twilio...")
        
        # Add .mp3 extension to get audio file
        if not recording_url.endswith('.mp3'):
            recording_url = recording_url + '.mp3'
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                recording_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            )
            
            if response.status_code == 200:
                logger.info(f"Downloaded recording: {len(response.content)} bytes")
                return response.content
            else:
                logger.error(f"Failed to download recording: {response.status_code}")
                return b""
        
    except Exception as e:
        logger.error(f"Recording download failed: {str(e)}")
        return b""


def end_call(message: str = "Thank you for your time. Have a great day!") -> VoiceResponse:
    """
    End call gracefully
    
    Args:
        message: Goodbye message
    
    Returns:
        TwiML to end call
    """
    response = VoiceResponse()
    response.say(message, voice='Polly.Joanna')
    response.hangup()
    return response


async def send_sms(to_number: str, message: str) -> Dict[str, Any]:
    """
    Send SMS via Twilio (optional feature)
    
    Args:
        to_number: Recipient phone number
        message: SMS text
    
    Returns:
        Message SID and status
    """
    try:
        message = twilio_client.messages.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=message
        )
        
        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status
        }
        
    except Exception as e:
        logger.error(f"SMS send failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }



