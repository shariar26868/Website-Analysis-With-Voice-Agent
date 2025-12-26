# """
# Transcription and Summarization Service
# """
# import openai
# from typing import Optional, Dict, List
# from app.config import settings
# from app.utils import logger

# # Initialize OpenAI client
# openai.api_key = settings.OPENAI_API_KEY


# async def transcribe_audio(audio_data: bytes) -> Optional[str]:
#     """
#     Transcribe audio using OpenAI Whisper API
    
#     Args:
#         audio_data: Audio file bytes (mp3)
    
#     Returns:
#         Transcribed text
#     """
#     try:
#         logger.info("Transcribing audio with Whisper...")
        
#         # Save temporarily to pass to Whisper
#         import tempfile
#         with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
#             temp_file.write(audio_data)
#             temp_path = temp_file.name
        
#         # Transcribe with Whisper
#         with open(temp_path, "rb") as audio_file:
#             transcript = openai.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=audio_file,
#                 language="en"
#             )
        
#         # Clean up temp file
#         import os
#         os.unlink(temp_path)
        
#         logger.info(f"Transcription completed: {len(transcript.text)} characters")
#         return transcript.text
        
#     except Exception as e:
#         logger.error(f"Transcription failed: {str(e)}")
#         return None


# async def generate_summary_and_insights(transcript: str) -> Dict[str, any]:
#     """
#     Generate summary and extract key points using GPT-4
    
#     Args:
#         transcript: Call transcript text
    
#     Returns:
#         Dict with summary and key_points
#     """
#     try:
#         logger.info("Generating summary and insights...")
        
#         prompt = f"""Analyze this sales call transcript and provide:

# 1. A brief summary (2-3 sentences)
# 2. Key points discussed (as bullet points)
# 3. Any objections raised by the prospect
# 4. Next steps or action items

# Transcript:
# {transcript}

# Format your response as:
# SUMMARY: [summary here]
# KEY_POINTS: [point 1], [point 2], [point 3]
# OBJECTIONS: [objection 1], [objection 2]
# """
        
#         response = openai.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a sales call analyst."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=500
#         )
        
#         result = response.choices[0].message.content
        
#         # Parse response
#         summary = ""
#         key_points = []
#         objections = []
        
#         for line in result.split("\n"):
#             line = line.strip()
#             if line.startswith("SUMMARY:"):
#                 summary = line.replace("SUMMARY:", "").strip()
#             elif line.startswith("KEY_POINTS:"):
#                 points_text = line.replace("KEY_POINTS:", "").strip()
#                 key_points = [p.strip() for p in points_text.split(",") if p.strip()]
#             elif line.startswith("OBJECTIONS:"):
#                 obj_text = line.replace("OBJECTIONS:", "").strip()
#                 objections = [o.strip() for o in obj_text.split(",") if o.strip()]
        
#         logger.info("Summary and insights generated successfully")
        
#         return {
#             "summary": summary,
#             "key_points": key_points,
#             "objections": objections
#         }
        
#     except Exception as e:
#         logger.error(f"Summary generation failed: {str(e)}")
#         return {
#             "summary": None,
#             "key_points": [],
#             "objections": []
#         }


# async def process_recording(call_sid: str, audio_data: bytes) -> Dict[str, any]:
#     """
#     Complete processing: transcribe + summarize
    
#     Args:
#         call_sid: Twilio call SID
#         audio_data: Audio file bytes
    
#     Returns:
#         Dict with transcript, summary, key_points, objections
#     """
#     try:
#         # Step 1: Transcribe
#         transcript = await transcribe_audio(audio_data)
        
#         if not transcript:
#             logger.error("Transcription failed, skipping summary")
#             return {
#                 "transcript": None,
#                 "summary": None,
#                 "key_points": [],
#                 "objections": []
#             }
        
#         # Step 2: Generate insights
#         insights = await generate_summary_and_insights(transcript)
        
#         return {
#             "transcript": transcript,
#             "summary": insights.get("summary"),
#             "key_points": insights.get("key_points", []),
#             "objections": insights.get("objections", [])
#         }
        
#     except Exception as e:
#         logger.error(f"Recording processing failed: {str(e)}")
#         return {
#             "transcript": None,
#             "summary": None,
#             "key_points": [],
#             "objections": []
#         }




"""
Transcription and Summarization Service
"""
import openai
from typing import Optional, Dict, List
from app.config import settings
from app.utils import logger

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY


async def transcribe_audio(audio_data: bytes) -> Optional[str]:
    """
    Transcribe audio using OpenAI Whisper API
    
    Args:
        audio_data: Audio file bytes (mp3)
    
    Returns:
        Transcribed text
    """
    try:
        logger.info("Transcribing audio with Whisper...")
        
        # Save temporarily to pass to Whisper
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # Transcribe with Whisper
        with open(temp_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        
        # Clean up temp file
        import os
        os.unlink(temp_path)
        
        logger.info(f"Transcription completed: {len(transcript.text)} characters")
        return transcript.text
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return None


async def generate_summary_and_insights(transcript: str) -> Dict[str, any]:
    """
    Generate summary and extract key points using GPT-4
    
    Args:
        transcript: Call transcript text
    
    Returns:
        Dict with summary and key_points
    """
    try:
        # ✅ NEW: Check if transcript is too short
        if len(transcript.strip()) < 50:
            logger.warning(f"Transcript too short ({len(transcript)} chars), skipping summary generation")
            return {
                "summary": "Transcript too short to generate meaningful summary",
                "key_points": [],
                "objections": []
            }
        
        # ✅ NEW: Check if it's a Twilio trial message
        if "trial account" in transcript.lower():
            logger.warning("Detected Twilio trial account message, skipping summary generation")
            return {
                "summary": "Twilio trial account message detected - not a real conversation",
                "key_points": ["Upgrade Twilio account to remove trial messages"],
                "objections": []
            }
        
        logger.info("Generating summary and insights...")
        
        prompt = f"""Analyze this sales call transcript and provide:

1. A brief summary (2-3 sentences)
2. Key points discussed (as bullet points)
3. Any objections raised by the prospect
4. Next steps or action items

Transcript:
{transcript}

Format your response as:
SUMMARY: [summary here]
KEY_POINTS: [point 1], [point 2], [point 3]
OBJECTIONS: [objection 1], [objection 2]
"""
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a sales call analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        
        # Parse response
        summary = ""
        key_points = []
        objections = []
        
        for line in result.split("\n"):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("KEY_POINTS:"):
                points_text = line.replace("KEY_POINTS:", "").strip()
                key_points = [p.strip() for p in points_text.split(",") if p.strip()]
            elif line.startswith("OBJECTIONS:"):
                obj_text = line.replace("OBJECTIONS:", "").strip()
                objections = [o.strip() for o in obj_text.split(",") if o.strip()]
        
        logger.info("Summary and insights generated successfully")
        
        return {
            "summary": summary,
            "key_points": key_points,
            "objections": objections
        }
        
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        return {
            "summary": None,
            "key_points": [],
            "objections": []
        }


async def process_recording(call_sid: str, audio_data: bytes) -> Dict[str, any]:
    """
    Complete processing: transcribe + summarize
    
    Args:
        call_sid: Twilio call SID
        audio_data: Audio file bytes
    
    Returns:
        Dict with transcript, summary, key_points, objections
    """
    try:
        # Step 1: Transcribe
        transcript = await transcribe_audio(audio_data)
        
        if not transcript:
            logger.error("Transcription failed, skipping summary")
            return {
                "transcript": None,
                "summary": None,
                "key_points": [],
                "objections": []
            }
        
        # Step 2: Generate insights
        insights = await generate_summary_and_insights(transcript)
        
        return {
            "transcript": transcript,
            "summary": insights.get("summary"),
            "key_points": insights.get("key_points", []),
            "objections": insights.get("objections", [])
        }
        
    except Exception as e:
        logger.error(f"Recording processing failed: {str(e)}")
        return {
            "transcript": None,
            "summary": None,
            "key_points": [],
            "objections": []
        }