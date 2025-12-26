"""
Sara AI Agent - Conversation Orchestration
"""
from typing import Dict, Any, List
from datetime import datetime
from bson import ObjectId

from app.config import get_db, settings
from app.models import CallLog, CallStatus, CallOutcome
from app.services.twilio_service import make_call, create_voice_response, end_call
from app.services.openai_service import generate_sara_response, summarize_conversation
from app.utils import logger

# In-memory conversation storage (for active calls)
active_conversations: Dict[str, List[Dict[str, str]]] = {}


async def initiate_sara_call(lead_id: str, lead_data: Dict[str, Any], phone_number: str):
    """
    Initiate Sara call to a lead
    
    This is the main entry point for Sara calls
    
    Flow:
    1. Create call log in database
    2. Make Twilio call
    3. Twilio will call our webhook
    4. Sara conversation starts
    """
    try:
        logger.info(f"Sara initiating call to: {phone_number}")
        
        db = get_db()
        
        # Create call log
        call_log = CallLog(
            lead_id=lead_id,
            phone_number=phone_number,
            status=CallStatus.PENDING,
            started_at=datetime.utcnow()
        )
        
        result = await db.call_logs.insert_one(call_log.model_dump())
        call_log_id = str(result.inserted_id)
        
        # Prepare webhook URL (this should be your public URL)
        webhook_url = f"https://richelle-nonfictive-derivationally.ngrok-free.dev/api/v1/webhooks/twilio/voice?lead_id={lead_id}&call_log_id={call_log_id}"
        status_callback = f"https://richelle-nonfictive-derivationally.ngrok-free.dev/api/v1/webhooks/twilio/status"
        
        # Make call via Twilio
        call_result = await make_call(
            to_number=phone_number,
            webhook_url=webhook_url,
            status_callback_url=status_callback
        )
        
        if call_result.get("success"):
            # Update call log with Twilio SID
            await db.call_logs.update_one(
                {"_id": ObjectId(call_log_id)},
                {
                    "$set": {
                        "call_sid": call_result["call_sid"],
                        "status": CallStatus.IN_PROGRESS
                    }
                }
            )
            
            logger.info(f"Call initiated successfully: {call_result['call_sid']}")
        else:
            # Update as failed
            await db.call_logs.update_one(
                {"_id": ObjectId(call_log_id)},
                {
                    "$set": {
                        "status": CallStatus.FAILED,
                        "ended_at": datetime.utcnow()
                    }
                }
            )
            
            logger.error(f"Call initiation failed: {call_result.get('error')}")
        
    except Exception as e:
        logger.error(f"Sara call initiation failed: {str(e)}")


async def start_conversation(call_sid: str, call_data: Dict[str, Any]):
    """
    Start Sara conversation when call is answered
    
    This is called by Twilio webhook when call connects
    """
    try:
        logger.info(f"Starting Sara conversation: {call_sid}")
        
        # Get lead data from database
        lead_id = call_data.get("lead_id")
        
        if not lead_id:
            logger.error("No lead_id in call data")
            return end_call("Sorry, there was an error. Goodbye.")
        
        db = get_db()
        lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
        
        if not lead:
            logger.error(f"Lead not found: {lead_id}")
            return end_call("Sorry, there was an error. Goodbye.")
        
        # Initialize conversation history
        active_conversations[call_sid] = []
        
        # Generate Sara's opening message
        opening_message = f"""
Hi, this is Sara from TruFindAI. 
Am I speaking with someone from {lead.get('business_name')}? 
I noticed your website has some AI visibility issues that are preventing 
search engines and AI assistants like ChatGPT from properly understanding your business. 
Do you have a moment to discuss how we can help fix this?
"""
        
        # Add to conversation history
        active_conversations[call_sid].append({
            "role": "assistant",
            "content": opening_message.strip()
        })
        
        # Create TwiML response
        response = create_voice_response(opening_message.strip(), gather_input=True)
        
        return response
        
    except Exception as e:
        logger.error(f"Start conversation failed: {str(e)}")
        return end_call("Sorry, there was an error. Goodbye.")


async def handle_voice_input(call_sid: str, user_speech: str):
    """
    Handle user's voice input during call
    
    This is called by Twilio webhook when user speaks
    
    Flow:
    1. Add user speech to conversation history
    2. Get lead context from database
    3. Generate Sara's response using GPT-4
    4. Return TwiML response
    """
    try:
        logger.info(f"User said: {user_speech[:100]}")
        
        # Get conversation history
        conversation = active_conversations.get(call_sid, [])
        
        # Add user message
        conversation.append({
            "role": "user",
            "content": user_speech
        })
        
        # Get lead data
        db = get_db()
        call_log = await db.call_logs.find_one({"call_sid": call_sid})
        
        if not call_log:
            logger.error("Call log not found")
            return end_call("Thank you for your time. Goodbye.")
        
        lead = await db.leads.find_one({"_id": ObjectId(call_log["lead_id"])})
        
        # Check if user wants to end call
        end_phrases = ["not interested", "no thank", "don't call", "goodbye", "bye", "hang up"]
        if any(phrase in user_speech.lower() for phrase in end_phrases):
            logger.info("User requested to end call")
            
            # Save conversation and outcome
            await save_call_outcome(
                call_sid=call_sid,
                conversation=conversation,
                outcome=CallOutcome.NOT_INTERESTED
            )
            
            return end_call("I understand. Thank you for your time. Have a great day!")
        
        # Generate Sara's response
        sara_response = await generate_sara_response(
            user_message=user_speech,
            lead_data=lead,
            conversation_history=conversation
        )
        
        # Add Sara's response to history
        conversation.append({
            "role": "assistant",
            "content": sara_response
        })
        
        # Update conversation in memory
        active_conversations[call_sid] = conversation
        
        # Save transcript to database periodically
        await save_transcript(call_sid, conversation)
        
        # Check if conversation should end (max 10 exchanges)
        if len(conversation) >= 20:  # 10 user + 10 Sara messages
            logger.info("Max conversation length reached")
            
            await save_call_outcome(
                call_sid=call_sid,
                conversation=conversation,
                outcome=CallOutcome.CALLBACK_NEEDED
            )
            
            return end_call("Thank you so much for your time. I'll send you more information via email. Have a great day!")
        
        # Continue conversation
        response = create_voice_response(sara_response, gather_input=True)
        
        return response
        
    except Exception as e:
        logger.error(f"Handle voice input failed: {str(e)}")
        return end_call("Sorry, there was a technical issue. Please visit trufindai.com for more information.")


async def save_transcript(call_sid: str, conversation: List[Dict[str, str]]):
    """Save conversation transcript to database"""
    try:
        db = get_db()
        
        # Format transcript
        transcript_lines = []
        for msg in conversation:
            role = "Sara" if msg["role"] == "assistant" else "Customer"
            transcript_lines.append(f"{role}: {msg['content']}")
        
        transcript_text = "\n\n".join(transcript_lines)
        
        # Update call log
        await db.call_logs.update_one(
            {"call_sid": call_sid},
            {"$set": {"transcript": transcript_text}}
        )
        
    except Exception as e:
        logger.error(f"Save transcript failed: {str(e)}")


async def save_call_outcome(
    call_sid: str,
    conversation: List[Dict[str, str]],
    outcome: CallOutcome
):
    """
    Save call outcome and summary
    
    This is called when call ends
    """
    try:
        logger.info(f"Saving call outcome: {outcome}")
        
        db = get_db()
        
        # Format transcript
        transcript_lines = []
        for msg in conversation:
            role = "Sara" if msg["role"] == "assistant" else "Customer"
            transcript_lines.append(f"{role}: {msg['content']}")
        
        transcript_text = "\n\n".join(transcript_lines)
        
        # Generate summary using AI
        summary = await summarize_conversation(transcript_text)
        
        # Update call log
        await db.call_logs.update_one(
            {"call_sid": call_sid},
            {
                "$set": {
                    "status": CallStatus.COMPLETED,
                    "outcome": outcome,
                    "transcript": transcript_text,
                    "conversation_summary": summary.get("summary"),
                    "key_points": summary.get("key_points", []),
                    "objections": summary.get("objections", []),
                    "ended_at": datetime.utcnow()
                }
            }
        )
        
        # Update lead status
        call_log = await db.call_logs.find_one({"call_sid": call_sid})
        if call_log:
            await db.leads.update_one(
                {"_id": ObjectId(call_log["lead_id"])},
                {
                    "$set": {
                        "call_status": CallStatus.COMPLETED,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        # Clean up in-memory conversation
        if call_sid in active_conversations:
            del active_conversations[call_sid]
        
        logger.info("Call outcome saved successfully")
        
    except Exception as e:
        logger.error(f"Save call outcome failed: {str(e)}")


