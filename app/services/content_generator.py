from openai import OpenAI
from typing import Dict
import logging
import os
import json

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_note_content",
                    "description": "Generate emoji, title, and summary from voice transcription.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "emoji": {
                                "type": "string",
                                "description": "A single emoji that captures the main theme, topic, or emotion of the note"
                            },
                            "title": {
                                "type": "string",
                                "description": "A clear, contextual title that reflects the note's content (max 50 characters)"
                            },
                            "summary": {
                                "type": "string",
                                "description": "A comprehensive summary that captures the key points, context, and significance of the transcription. Should be 2-3 paragraphs long and provide meaningful insights."
                            }
                        },
                        "required": ["emoji", "title", "summary"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]

    async def generate_content(self, transcription: str) -> Dict[str, str]:
        """
        Generate emoji, title, and summary from transcribed text
        """
        try:
            system_prompt = """You are an AI assistant specialized in processing voice notes.
            Your task is to:
            1. Choose a single emoji that best represents the note's theme or topic
            2. Create a clear, contextual title that reflects the content
            3. Generate a comprehensive summary that:
               - Captures the key points and main ideas
               - Provides essential context and significance
               - Is 2-3 paragraphs long
               - Includes important details and implications
               - Makes the content clear and understandable
               
            Focus on creating a summary that helps readers quickly understand 
            the full context and importance of the voice note."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please process this voice note transcription: {transcription}"}
            ]

            response = self.client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=messages,
                tools=self.tools,
                tool_choice={"type": "function", "function": {"name": "generate_note_content"}},
                temperature=0.7
            )

            if not hasattr(response.choices[0].message, 'tool_calls') or not response.choices[0].message.tool_calls:
                raise ValueError("No function call received from the model")

            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name != "generate_note_content":
                raise ValueError(f"Unexpected function call: {tool_call.function.name}")

            try:
                content = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse function arguments: {e}")

            required_fields = ["emoji", "title", "summary"]
            for field in required_fields:
                if field not in content:
                    raise ValueError(f"Missing required field: {field}")

            return {
                "emoji": content["emoji"],
                "title": content["title"],
                "transcription": transcription,  # Original transcription
                "summary": content["summary"]    # Generated summary
            }

        except Exception as e:
            logger.error(f"Error in generate_content: {str(e)}")
            raise ValueError(f"Failed to generate content: {str(e)}") 