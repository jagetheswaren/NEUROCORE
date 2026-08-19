from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from server.api.dependencies import get_orchestrator

router = APIRouter(prefix="/voice", tags=["Voice"])

class TTSRequest(BaseModel):
    text: str
    output_filename: Optional[str] = "api_tts_output.wav"

@router.post("/speak")
def speak_endpoint(req: TTSRequest, orchestrator=Depends(get_orchestrator)):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    if not orchestrator.tts:
        return {
            "status": "warning",
            "message": "TTS engine not loaded on server.",
            "audio_file": None
        }

    try:
        output_path = orchestrator.tts.speak(req.text, req.output_filename)
        return {
            "status": "success",
            "text": req.text,
            "audio_file": str(output_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Generation Error: {e}")

@router.get("/status")
def voice_status(orchestrator=Depends(get_orchestrator)):
    return {
        "speech_recognizer": "ready" if orchestrator.speech else "disabled",
        "text_to_speech": "ready" if orchestrator.tts else "disabled"
    }
