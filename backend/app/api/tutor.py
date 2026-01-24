"""
AI Tutor API Routes

Provides endpoints for the AI Tutor chat interface with voice support.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import json

from app.services.tutor_service import TutorService, DeepgramTTS
from app.config import settings

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])

# Initialize services
tutor_service = TutorService()
tts_service = DeepgramTTS()

# In-memory session storage (use Redis in production)
sessions: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI tutor response")
    session_id: str = Field(..., description="Session ID for future messages")
    should_generate_video: bool = Field(False, description="Whether to trigger video generation")
    video_prompt: Optional[str] = Field(None, description="Prompt for video generation if triggered")
    modify_video: bool = Field(False, description="Whether this is a video modification request")
    modifications: Optional[Dict[str, Any]] = Field(None, description="Video modifications if requested")


class TTSRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Text to convert to speech")
    voice: str = Field("aura-asteria-en", description="Voice model to use")


class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: str
    accent: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the AI tutor and get a response.
    
    The tutor will:
    - Provide educational explanations in markdown format
    - Detect when visual explanation would help and suggest video generation
    - Detect modification requests for existing videos
    """
    message = request.message.strip()
    
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = sessions.get(session_id, {"history": [], "video_context": None})
    
    # Process message through tutor service
    try:
        result = await tutor_service.chat(
            message=message,
            conversation_history=session["history"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tutor service error: {str(e)}")
    
    # Update session history
    session["history"].append({"role": "user", "content": message})
    session["history"].append({"role": "assistant", "content": result["response"]})
    
    # Keep history manageable (last 20 messages)
    if len(session["history"]) > 20:
        session["history"] = session["history"][-20:]
    
    # Store video context if video is being generated
    if result.get("should_generate_video") or result.get("modify_video"):
        session["video_context"] = {
            "prompt": result.get("video_prompt"),
            "modifications": result.get("modifications")
        }
        tutor_service.set_video_context(session["video_context"])
    
    sessions[session_id] = session
    
    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        should_generate_video=result.get("should_generate_video", False),
        video_prompt=result.get("video_prompt"),
        modify_video=result.get("modify_video", False),
        modifications=result.get("modifications")
    )


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Deepgram TTS.
    
    Returns audio/mpeg content that can be played directly.
    """
    text = request.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Synthesize speech
    audio_bytes = await tts_service.synthesize(
        text=text,
        voice=request.voice,
        encoding="mp3"
    )
    
    if not audio_bytes:
        raise HTTPException(
            status_code=503, 
            detail="Text-to-speech service unavailable. Check Deepgram API key."
        )
    
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"}
    )


@router.get("/voices", response_model=List[VoiceInfo])
async def get_voices():
    """
    Get available TTS voices.
    """
    return tts_service.get_available_voices()


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get conversation history for a session.
    """
    session = sessions.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "history": session["history"],
        "video_context": session.get("video_context")
    }


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a conversation session.
    """
    if session_id in sessions:
        del sessions[session_id]
    
    tutor_service.clear_history()
    
    return {"message": "Session cleared", "session_id": session_id}
