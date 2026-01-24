"""AI Tutor API Routes with LaTeX support."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from app.services.tutor_service import TutorService, DeepgramTTS

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])

tutor_service = TutorService()
tts_service = DeepgramTTS()
sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=4000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    should_generate_video: bool = False
    video_prompt: Optional[str] = None
    modify_video: bool = False
    modifications: Optional[Dict[str, Any]] = None


class TTSRequest(BaseModel):
    text: str = Field(..., max_length=5000)
    voice: str = "aura-asteria-en"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the AI tutor. Supports LaTeX in responses."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    session_id = request.session_id or str(uuid.uuid4())
    session = sessions.get(session_id, {"history": [], "video_context": None})
    
    try:
        result = await tutor_service.chat(message, session["history"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    session["history"].append({"role": "user", "content": message})
    session["history"].append({"role": "assistant", "content": result["response"]})
    
    if len(session["history"]) > 20:
        session["history"] = session["history"][-20:]
    
    if result.get("should_generate_video") or result.get("modify_video"):
        session["video_context"] = {"prompt": result.get("video_prompt")}
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
    """Convert text to speech. LaTeX is cleaned for natural speech."""
    audio = await tts_service.synthesize(request.text, request.voice)
    if not audio:
        raise HTTPException(status_code=503, detail="TTS unavailable")
    return Response(content=audio, media_type="audio/mpeg")


@router.get("/voices")
async def get_voices():
    return tts_service.get_available_voices()


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    tutor_service.clear_history()
    return {"message": "Session cleared"}
