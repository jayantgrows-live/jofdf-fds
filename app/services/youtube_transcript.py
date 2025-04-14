import aiohttp
import ssl
import certifi
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs

async def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various forms of YouTube URLs."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed_url.path[1:]
        if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        return None
    except Exception:
        return None

async def fetch_youtube_transcript(video_id: str, format: bool = True) -> Dict:
    """
    Fetch YouTube transcript using the kome.ai API.
    
    Args:
        video_id: YouTube video ID
        format: Boolean to indicate if the transcript should be formatted
        
    Returns:
        Dict containing the transcript response
    """
    api_url = "https://api.kome.ai/api/tools/youtube-transcripts"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://kome.ai",
        "referer": "https://kome.ai/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    
    payload = {
        "video_id": video_id,
        "format": format
    }
    
    # Create SSL context with proper certificate verification
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch transcript. Status: {response.status}, Error: {error_text}")
    except aiohttp.ClientError as e:
        raise Exception(f"Network error occurred: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}") 