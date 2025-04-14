# Voice Note AI Backend

A FastAPI backend service for processing voice notes using AI. The service transcribes audio to text and generates relevant content using AI models.

## Features

- Audio transcription using Groq API
- YouTube video transcript processing
- AI-powered content generation using Gemini AI
- Generates emoji, title, and summary for each voice note
- Support for multiple audio formats
- API key authentication
- Error handling and validation
- Docker support for easy deployment

## Setup

### Using Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file in the root directory with your API keys:
```bash
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
API_KEY=your_api_key_here  # For API authentication
```

3. Build and start the containers:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys (see above)

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## Authentication

The API uses Bearer token authentication. Include the API key in the Authorization header:

```bash
Authorization: Bearer your_api_key_here
```

## API Endpoints

### GET /

Root endpoint that returns API information.

**Request:**
- Method: GET
- Headers: Authorization: Bearer your_api_key_here

**Response:**
```json
{
    "message": "server is running"
}
```

### GET /health

Health check endpoint (no authentication required).

**Response:**
```json
{
    "status": "healthy"
}
```

### POST /api/v1/voice-notes

Process a voice note file and return transcription with AI-generated content.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Headers: Authorization: Bearer your_api_key_here
- Body: file (audio file)

**Response:**
```json
{
    "transcription": "string",
    "emoji": "string",
    "title": "string",
    "summary": "string"
}
```

### POST /api/v1/youtube-notes

Process a YouTube video URL and return transcript with AI-generated content.

**Request:**
- Method: POST
- Content-Type: application/json
- Headers: Authorization: Bearer your_api_key_here
- Body:
```json
{
    "video_url": "https://www.youtube.com/watch?v=video_id"
}
```

**Response:**
```json
{
    "transcription": "string",
    "emoji": "string",
    "title": "string",
    "summary": "string"
}
```

## Supported Audio Formats

- FLAC
- MP3
- MP4
- MPEG
- MPGA
- M4A
- OGG
- WAV
- WEBM

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 400: Bad Request (invalid file format, size too large)
- 401: Unauthorized (missing or invalid API key)
- 500: Internal Server Error (processing failed)

## Development

The project follows a modular structure:
```
app/
├── main.py
├── auth/
│   └── api_key.py
├── routers/
│   ├── voice_notes.py
│   └── youtube_notes.py
├── services/
│   ├── speech_handler.py
│   ├── content_generator.py
│   └── youtube_transcript.py
└── schemas/
    └── voice_note.py
```

## Docker Commands

- Build and start containers: `docker-compose up --build`
- Start existing containers: `docker-compose up`
- Stop containers: `docker-compose down`
- View logs: `docker-compose logs -f`
- Rebuild a specific service: `docker-compose up --build api` 