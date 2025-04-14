import requests
import os


# API configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("API_KEY", "vn-initial-key")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

def test_root():
    """Test root endpoint"""
    response = requests.get("http://localhost:8000/", headers=HEADERS)
    print("\nTesting Root Endpoint:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("API Information:")
        print(response.json())
    else:
        print(f"Error: {response.text}")

def test_voice_note():
    """Test voice note endpoint"""
    # Your test WAV file
    test_file = "test.wav"  # Replace with your WAV file path
    
    print("\nTesting Voice Note Endpoint:")
    # Send the request
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'audio/wav')}
        response = requests.post(f"{BASE_URL}/voice-notes", headers=HEADERS, files=files)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nAPI Response:")
        print(f"\nEmoji: {data['emoji']}")
        print(f"Title: {data['title']}")
        print(f"\nTranscription:")
        print("-" * 80)
        print(data['transcription'])
        print("-" * 80)
        print(f"\nSummary:")
        print("-" * 80)
        print(data['summary'])
        print("-" * 80)
    else:
        print(f"Error: {response.text}")

def test_youtube_note():
    """Test YouTube note endpoint"""
    # Test YouTube URL
    test_url = "https://www.youtube.com/watch?v=yeI_u8JIJXc"
    
    print("\nTesting YouTube Note Endpoint:")
    # Send the request
    response = requests.post(
        f"{BASE_URL}/youtube-notes",
        headers=HEADERS,
        json={"video_url": test_url}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nAPI Response:")
        print(f"\nEmoji: {data['emoji']}")
        print(f"Title: {data['title']}")
        print(f"\nTranscription:")
        print("-" * 80)
        print(data['transcription'])
        print("-" * 80)
        print(f"\nSummary:")
        print("-" * 80)
        print(data['summary'])
        print("-" * 80)
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    # Test all endpoints
    test_root()
    test_voice_note()
    test_youtube_note() 