from fastapi import APIRouter, HTTPException
from app.services.content_generator import ContentGenerator
from app.schemas.voice_note import YouTubeVideoRequest, YouTubeVideoResponse, ErrorResponse
from app.services.youtube_transcript import fetch_youtube_transcript, extract_video_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
content_generator = ContentGenerator()

@router.post("/youtube-notes",
            response_model=YouTubeVideoResponse,
            responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def process_youtube_video(request: YouTubeVideoRequest):
    """
    Process a YouTube video URL:
    1. Extract video ID and fetch transcript
    2. Generate emoji, title, and summary using AI
    """
    try:
        # Extract video ID and fetch transcript
        video_id = await extract_video_id(str(request.video_url))
        if not video_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL or could not extract video ID"
            )
        
        # Fetch transcript
        transcript_result = await fetch_youtube_transcript(video_id)
        if not transcript_result or not transcript_result.get("transcript"):
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch video transcript"
            )
        
        transcription = transcript_result["transcript"]
        
        # Generate content using AI
        content = await content_generator.generate_content(transcription)
        
        # Ensure all required fields are present
        required_fields = ["emoji", "title", "summary"]
        for field in required_fields:
            if field not in content:
                raise HTTPException(
                    status_code=500,
                    detail=f"Content generation failed: missing {field} field"
                )
        
        return YouTubeVideoResponse(
            emoji=content["emoji"],
            title=content["title"],
            transcription=transcription,
            summary=content["summary"]
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing YouTube video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 