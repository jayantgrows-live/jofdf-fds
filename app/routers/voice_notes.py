from fastapi import APIRouter, UploadFile, HTTPException
from app.services.speech_handler import SpeechHandler
from app.services.content_generator import ContentGenerator
from app.schemas.voice_note import VoiceNoteResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
speech_handler = SpeechHandler()
content_generator = ContentGenerator()

@router.post("/voice-notes", 
             response_model=VoiceNoteResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def process_voice_note(file: UploadFile):
    """
    Process a voice note file:
    1. Transcribe the audio to text
    2. Generate emoji, title, and summary using AI
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Transcribe audio
        transcription_result = await speech_handler.transcribe_audio(
            file_content=file_content,
            content_type=file.content_type
        )
        
        if not transcription_result.get("text"):
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        
        transcription = transcription_result["text"]
        
        # Generate content using AI
        content = await content_generator.generate_content(transcription)
        
        # Ensure all required fields are present
        required_fields = ["emoji", "title", "transcription", "summary"]
        for field in required_fields:
            if field not in content:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Content generation failed: missing {field} field"
                )
        
        return VoiceNoteResponse(
            emoji=content["emoji"],
            title=content["title"],
            transcription=content["transcription"],
            summary=content["summary"]
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing voice note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 