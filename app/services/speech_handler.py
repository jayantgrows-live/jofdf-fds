from fastapi import HTTPException
import aiohttp
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self):
        self.base_url = "https://api.groq.com/openai/v1/audio/transcriptions"
        self.supported_formats = ['flac', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'ogg', 'wav', 'webm']
        self.max_file_size = 25 * 1024 * 1024  # 25 MB in bytes
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

    def _validate_file_type(self, content_type: str) -> bool:
        """Validate if the file type is supported"""
        file_ext = content_type.split('/')[-1].lower()
        # Handle x-m4a case
        if file_ext == 'x-m4a':
            file_ext = 'm4a'
        return file_ext in self.supported_formats

    def _validate_file_size(self, file_size: int) -> bool:
        """Validate if the file size is within limits"""
        return file_size <= self.max_file_size

    async def transcribe_audio(
        self, 
        file_content: bytes,
        content_type: str,
        model: str = "whisper-large-v3",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0
    ) -> dict:
        """
        Transcribe audio file using Groq API
        """
        try:
            # Validate file type
            if not self._validate_file_type(content_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Supported formats: {', '.join(self.supported_formats)}"
                )

            # Validate file size
            if not self._validate_file_size(len(file_content)):
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of 25MB"
                )

            # Prepare the API request
            url = f"{self.base_url}"
            
            # Convert content type from x-m4a to m4a
            actual_content_type = "audio/m4a" if content_type == "audio/x-m4a" else content_type
            
            # Prepare form data with proper extension
            extension = actual_content_type.split('/')[-1]
            if extension == 'x-m4a':
                extension = 'm4a'
            
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file', 
                file_content, 
                filename=f'audio_file.{extension}',
                content_type=actual_content_type
            )
            form_data.add_field('model', model)
            
            if language:
                form_data.add_field('language', language)
            if prompt:
                form_data.add_field('prompt', prompt)
            if response_format:
                form_data.add_field('response_format', response_format)
            if temperature is not None:
                form_data.add_field('temperature', str(temperature))

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form_data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq API error: {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Error from Groq API: {error_text}"
                        )
                    
                    result = await response.json()
                    return result

        except Exception as e:
            logger.error(f"Error in transcribe_audio: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 