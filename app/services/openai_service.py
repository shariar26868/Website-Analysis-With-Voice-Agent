"""
OpenAI Service - GPT, Whisper, TTS Integration
"""
from openai import AsyncOpenAI
from typing import Dict, Any, List
import base64

from app.config import settings
from app.utils import logger

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_chat_response(
    messages: List[Dict[str, str]],
    system_prompt: str = None,
    temperature: float = 0.7
) -> str:
    """
    Generate chat response using GPT-4
    
    Args:
        messages: Conversation history
        system_prompt: System instructions
        temperature: Creativity level (0-1)
    
    Returns:
        AI response text
    """
    try:
        # Prepare messages
        full_messages = []
        
        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        full_messages.extend(messages)
        
        logger.info("Generating GPT-4 response...")
        
        # Call GPT-4
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4o" for better quality
            messages=full_messages,
            temperature=temperature,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"Generated response: {ai_response[:100]}...")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"GPT-4 generation failed: {str(e)}")
        return "I apologize, but I'm having trouble processing that right now."


async def transcribe_audio(audio_data: bytes, language: str = "en") -> str:
    """
    Transcribe audio using Whisper
    
    Args:
        audio_data: Audio file bytes
        language: Language code
    
    Returns:
        Transcribed text
    """
    try:
        logger.info("Transcribing audio with Whisper...")
        
        # Save audio temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        # Transcribe
        with open(temp_audio_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        
        # Cleanup
        import os
        os.unlink(temp_audio_path)
        
        logger.info(f"Transcription: {transcript.text[:100]}...")
        return transcript.text
        
    except Exception as e:
        logger.error(f"Whisper transcription failed: {str(e)}")
        return ""


async def text_to_speech(text: str, voice: str = "nova") -> bytes:
    """
    Convert text to speech using OpenAI TTS
    
    Args:
        text: Text to convert
        voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Audio bytes (MP3)
    """
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=1.0
        )
        
        audio_bytes = response.content
        logger.info(f"Generated audio: {len(audio_bytes)} bytes")
        
        return audio_bytes
        
    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        return b""


async def generate_sara_response(
    user_message: str,
    lead_data: Dict[str, Any],
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    Generate Sara's response based on lead context
    
    Args:
        user_message: What the user said
        lead_data: Lead information from database
        conversation_history: Previous conversation
    
    Returns:
        Sara's response
    """
    try:
        # Build Sara's context
        system_prompt = f"""
You are Sara, an AI sales agent for TruFindAI. You're calling to help businesses improve their AI visibility.

LEAD CONTEXT:
- Business: {lead_data.get('business_name')}
- Industry: {lead_data.get('industry', 'General')}
- Website: {lead_data.get('website_url')}
- AI Visibility Score: {lead_data.get('ai_visibility_score', 0)}/100
- Top Issues: {', '.join(lead_data.get('top_issues', [])[:3])}

YOUR GOAL:
Help them understand why AI visibility matters and offer our solution:
- $199 one-time setup
- $39/month ongoing optimization

CONVERSATION STYLE:
- Warm and professional
- Listen actively to their concerns
- Don't be pushy
- Focus on value, not price
- If they're not interested, politely end the call

IMPORTANT:
- Keep responses under 50 words
- Ask one question at a time
- Handle objections with empathy
"""

        # Add user message to history
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]
        
        # Generate response
        response = await generate_chat_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Sara response generation failed: {str(e)}")
        return "I appreciate your time today. Feel free to visit our website at trufindai.com to learn more."


async def summarize_conversation(transcript: str) -> Dict[str, Any]:
    """
    Summarize call conversation and extract key points
    
    Returns:
        - summary: Brief conversation summary
        - outcome: Call outcome
        - key_points: Important discussion points
        - objections: Customer objections raised
        - next_steps: Recommended follow-up
    """
    try:
        logger.info("Summarizing conversation...")
        
        prompt = f"""
Analyze this sales call transcript and provide a JSON summary.

Transcript:
{transcript}

Provide a JSON response with:
{{
  "summary": "Brief 2-3 sentence summary",
  "outcome": "success|callback_needed|not_interested|no_answer",
  "interest_level": "high|medium|low|none",
  "key_points": ["list of key discussion points"],
  "objections": ["list of objections raised"],
  "next_steps": "recommended follow-up action"
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sales call analyst. Analyze conversations and extract actionable insights. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        summary = json.loads(response.choices[0].message.content)
        
        return summary
        
    except Exception as e:
        logger.error(f"Conversation summarization failed: {str(e)}")
        return {
            "summary": "Summary unavailable",
            "outcome": "unknown",
            "key_points": [],
            "objections": []
        }