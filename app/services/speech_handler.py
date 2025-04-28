from fastapi import HTTPException
import logging
from typing import Optional
import os
import base64
from openai import OpenAI

logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Map of MIME types to their corresponding format names for Google API
        self.supported_formats = {
            'audio/wav': 'wav',
            'audio/mp3': 'mp3',
            'audio/aiff': 'aiff',
            'audio/aac': 'aac',
            'audio/ogg': 'ogg',
            'audio/flac': 'flac',
            # Additional common MIME type variations
            'audio/x-wav': 'wav',
            'audio/mpeg': 'mp3',
            'audio/mpeg3': 'mp3',
            'audio/x-aiff': 'aiff',
            'audio/x-aac': 'aac',
            'audio/vorbis': 'ogg',
            'audio/x-flac': 'flac'
        }
        self.max_file_size = 25 * 1024 * 1024  # 25 MB in bytes

    def _validate_file_type(self, content_type: str) -> tuple[bool, str]:
        """
        Validate if the file type is supported
        Returns: (is_valid, format_name)
        """
        return content_type in self.supported_formats, self.supported_formats.get(content_type, '')

    def _validate_file_size(self, file_size: int) -> bool:
        """Validate if the file size is within limits"""
        return file_size <= self.max_file_size

    async def transcribe_audio(
        self, 
        file_content: bytes,
        content_type: str,
        model: str = "gemini-2.0-flash",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0
    ) -> dict:
        """
        Transcribe audio file using Google's Gemini API
        """
        try:
            # Validate file type
            is_valid_type, format_name = self._validate_file_type(content_type)
            if not is_valid_type:
                supported_types = ", ".join(sorted(set(self.supported_formats.values())))
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Supported formats: {supported_types}"
                )

            # Validate file size
            if not self._validate_file_size(len(file_content)):
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of 25MB"
                )

            # Convert audio to base64
            base64_audio = base64.b64encode(file_content).decode('utf-8')

            # Prepare the transcription request
            transcription_prompt = prompt if prompt else "Transcribe this audio. Please provide the transcription in a clear format."
            
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": transcription_prompt,
                                },
                                {
                                    "type": "input_audio",
                                    "input_audio": {
                                        "data": base64_audio,
                                        "format": format_name
                                    }
                                }
                            ],
                        }
                    ],
                    temperature=temperature
                )

                if not response.choices or not response.choices[0].message.content:
                    raise HTTPException(
                        status_code=500,
                        detail="No transcription received from the model"
                    )

                # Return in the same format as before
                return {
                    "text": response.choices[0].message.content.strip()
                }

            except Exception as e:
                logger.error(f"Google API error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error from Google API: {str(e)}"
                )

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 
