from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests
from dotenv import load_dotenv
import os
import sqlite3
import json
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for React frontend

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_cache (
            video_id TEXT PRIMARY KEY,
            briefing TEXT,
            theme_alerts TEXT,
            recaps TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_video_id(url):
    """Extract video ID from YouTube URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
    return None

def chunk_transcript(transcript, chunk_duration=150):
    """Chunk transcript into 2-3 minute segments (default 150 seconds)."""
    chunks = []
    current_chunk = []
    current_duration = 0
    current_start = 0

    for entry in transcript:
        duration = entry['duration']
        if current_duration + duration <= chunk_duration:
            current_chunk.append(entry)
            current_duration += duration
        else:
            chunks.append({
                'start': current_start,
                'end': current_start + current_duration,
                'text': ' '.join([e['text'] for e in current_chunk])
            })
            current_chunk = [entry]
            current_start += current_duration
            current_duration = duration
    if current_chunk:
        chunks.append({
            'start': current_start,
            'end': current_start + current_duration,
            'text': ' '.join([e['text'] for e in current_chunk])
        })
    return chunks

def get_gemini_response(transcript_chunks):
    """Make a single request to Gemini API with structured prompt."""
    prompt = """
    You are an expert film analyst tasked with enhancing the viewing experience of a YouTube video by providing spoiler-free context and insights. Given the transcript of the video, provide the following in JSON format:

    1. **briefing**: A short (100-150 words), spoiler-free summary of the video's context, themes, or emotional tone to prepare the viewer without revealing plot details.
    2. **theme_alerts**: A list of objects, each containing:
       - **timestamp**: The approximate start time (in seconds) of a significant scene.
       - **theme**: The primary theme (e.g., "friendship", "conflict", "hope").
       - **emotion**: The dominant emotion (e.g., "joy", "tension", "sadness").
       - **description**: A brief (20-30 words), spoiler-free description of the scene's significance.
    3. **recaps**: A list of objects for each 2-3 minute segment, containing:
       - **timestamp_start**: Start time of the segment (in seconds).
       - **timestamp_end**: End time of the segment (in seconds).
       - **summary**: A short (50-70 words), spoiler-free summary of what happened in the segment, focusing on themes and emotions.

    Here is the transcript, divided into 2-3 minute chunks:
    {}
    
    Ensure all outputs are spoiler-free and focus on thematic and emotional insights. Return the response in JSON format.
    """.format(json.dumps(transcript_chunks, indent=2))

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return {"error": f"Gemini API error: {str(e)}"}

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    video_id = get_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # Check cache
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("SELECT briefing, theme_alerts, recaps FROM video_cache WHERE video_id = ?", (video_id,))
    cached = cursor.fetchone()
    if cached:
        conn.close()
        return jsonify({
            "briefing": cached[0],
            "theme_alerts": json.loads(cached[1]),
            "recaps": json.loads(cached[2])
        })

    # Fetch transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except (TranscriptsDisabled, NoTranscriptFound):
        conn.close()
        return jsonify({"error": "Transcript not available for this video"}), 400
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Transcript fetch error: {str(e)}"}), 500

    # Chunk transcript
    transcript_chunks = chunk_transcript(transcript)

    # Get Gemini response
    gemini_response = get_gemini_response(transcript_chunks)
    if isinstance(gemini_response, dict) and "error" in gemini_response:
        conn.close()
        return jsonify(gemini_response), 500

    try:
        # Parse Gemini response (assuming it returns JSON string)
        result = json.loads(gemini_response.strip('```json\n').strip('```'))
        briefing = result.get('briefing', '')
        theme_alerts = result.get('theme_alerts', [])
        recaps = result.get('recaps', [])

        # Cache results
        cursor.execute("""
            INSERT OR REPLACE INTO video_cache (video_id, briefing, theme_alerts, recaps)
            VALUES (?, ?, ?, ?)
        """, (video_id, briefing, json.dumps(theme_alerts), json.dumps(recaps)))
        conn.commit()
        conn.close()

        return jsonify({
            "briefing": briefing,
            "theme_alerts": theme_alerts,
            "recaps": recaps
        })
    except json.JSONDecodeError:
        conn.close()
        return jsonify({"error": "Invalid response from Gemini API"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)