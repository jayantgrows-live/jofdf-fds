from pydantic import BaseModel, HttpUrl
from typing import Optional

class VoiceNoteResponse(BaseModel):
    emoji: str
    title: str
    transcription: str
    summary: str

class ErrorResponse(BaseModel):
    detail: str

class YouTubeVideoRequest(BaseModel):
    video_url: HttpUrl

class YouTubeVideoResponse(BaseModel):
    emoji: str
    title: str
    transcription: str
    summary: str 