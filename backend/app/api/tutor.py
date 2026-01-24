"""AI Tutor API Routes - Visual-Synchronized Tutoring with LaTeX support."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from app.services.tutor_service import TutorService, DeepgramTTS
from app.services.visual_state import get_visual_state, clear_visual_state, VisualObjectType
from app.services.sync_orchestrator import get_sync_orchestrator

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
    visual_state: Optional[Dict[str, Any]] = None  # Current visual objects


class VisualStateUpdate(BaseModel):
    """Update visual state after rendering completes."""
    session_id: str
    scene_data: Dict[str, Any]


class TTSRequest(BaseModel):
    text: str = Field(..., max_length=5000)
    voice: str = "aura-asteria-en"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the visual-synchronized AI tutor.
    
    The tutor will ONLY describe visuals that are confirmed in the visual state.
    Supports LaTeX in responses.
    """
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    session_id = request.session_id or str(uuid.uuid4())
    session = sessions.get(session_id, {"history": [], "video_context": None})
    
    # Set session on tutor service for visual state tracking
    tutor_service.set_session(session_id)
    
    try:
        result = await tutor_service.chat(
            message, 
            session["history"],
            session_id=session_id
        )
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
    
    # Include current visual state in response
    visual_state = get_visual_state(session_id)
    visual_state_data = visual_state.get_state_for_tutor() if visual_state else None
    
    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        should_generate_video=result.get("should_generate_video", False),
        video_prompt=result.get("video_prompt"),
        modify_video=result.get("modify_video", False),
        modifications=result.get("modifications"),
        visual_state=visual_state_data
    )


@router.post("/visual-state/update")
async def update_visual_state(request: VisualStateUpdate):
    """
    Update visual state after Manim rendering completes.
    
    This is called by the renderer to confirm what is now visible.
    The tutor can only describe objects after this endpoint is called.
    """
    visual_state = get_visual_state(request.session_id)
    
    # Populate state from rendered scene
    visual_state._populate_from_scene(request.scene_data)
    
    return {
        "status": "updated",
        "session_id": request.session_id,
        "visible_objects": len(visual_state.visible_objects),
        "state": visual_state.get_state_for_tutor()
    }


@router.get("/visual-state/{session_id}")
async def get_session_visual_state(session_id: str):
    """Get the current visual state for a session."""
    visual_state = get_visual_state(session_id)
    return {
        "session_id": session_id,
        "state": visual_state.get_state_for_tutor(),
        "context_prompt": visual_state.generate_visual_context_prompt()
    }


@router.post("/visual-state/{session_id}/add-object")
async def add_visual_object(
    session_id: str,
    object_type: str,
    description: str,
    object_id: Optional[str] = None,
    color: Optional[str] = None,
    label: Optional[str] = None,
    math_expression: Optional[str] = None
):
    """Manually add a visual object to the state (for testing/debugging)."""
    visual_state = get_visual_state(session_id)
    
    try:
        obj_type = VisualObjectType(object_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid object type: {object_type}")
    
    obj = visual_state.add_object(
        obj_type,
        description,
        object_id=object_id,
        color=color,
        label=label,
        math_expression=math_expression
    )
    
    return {
        "status": "added",
        "object": {
            "id": obj.object_id,
            "type": obj.object_type.value,
            "description": obj.to_description()
        }
    }


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
    """Clear session including visual state."""
    if session_id in sessions:
        del sessions[session_id]
    clear_visual_state(session_id)
    tutor_service.clear_history()
    return {"message": "Session cleared"}
