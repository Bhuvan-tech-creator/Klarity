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
CORS(app, resources={r"/process_video": {"origins": "http://localhost:3000"}})

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
FREE_MOVIES = {
    "action": ["vKQi3bBA1y8", "8fT-l0YYLHI"],  # The Matrix, Inception trailers
    "comedy": ["dQw4w9WgXcQ"],  # Example (placeholder)
    "thriller": ["yoVq9Z2n_Rg"],  # Example (placeholder)
    "horror": ["o-0hcF97wy0"]  # Example (placeholder)
}  # Curated free YouTube video IDs

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_complexity (
            user_id TEXT PRIMARY KEY,
            clicks INTEGER DEFAULT 0,
            complexity_score REAL DEFAULT 1.0
        )
    """)
    cursor.execute("PRAGMA table_info(video_cache)")
    columns = [row[1] for row in cursor.fetchall()]
    if "rating" not in columns or "complexity" not in columns:
        if "rating" not in columns:
            cursor.execute("ALTER TABLE video_cache ADD COLUMN rating TEXT")
        if "complexity" not in columns:
            cursor.execute("ALTER TABLE video_cache ADD COLUMN complexity TEXT")
    conn.commit()
    conn.close()

init_db()

def get_video_id(url):
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

def get_gemini_response(transcript_chunks, complexity_score):
    prompt = f"""
    Recommend 4 free YouTube movies (provide video IDs) based on a complexity score of {complexity_score} (1.0 is low, 5.0 is high). Include 1 each from action, comedy, thriller, and horror genres. Keep it concise, no extra details.
    """
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return {"error": f"Gemini API error: {str(e)}"}

def update_complexity_score(user_id, click_count):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_complexity (user_id, clicks, complexity_score) VALUES (?, ?, ?)",
                   (user_id, click_count, max(1.0, 5.0 - (click_count * 0.1))))
    conn.commit()
    conn.close()

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    user_id = data.get('user_id', 'default_user')
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

    # Fetch transcript and process
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except (TranscriptsDisabled, NoTranscriptFound):
        conn.close()
        return jsonify({"error": "Transcript not available for this video"}), 400
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Transcript fetch error: {str(e)}"}), 500

    transcript_chunks = chunk_transcript(transcript)
    gemini_response = get_gemini_response(transcript_chunks, 1.0)  # Placeholder complexity
    if isinstance(gemini_response, dict) and "error" in gemini_response:
        conn.close()
        return jsonify(gemini_response), 500

    try:
        result = json.loads(gemini_response.strip('```json\n').strip('```'))
        briefing = result.get('briefing', '')
        theme_alerts = result.get('theme_alerts', [])
        recaps = result.get('recaps', [])

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

@app.route('/update_clicks', methods=['POST'])
def update_clicks():
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    click_count = data.get('clicks', 0)
    update_complexity_score(user_id, click_count)
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("SELECT complexity_score FROM user_complexity WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()[0]
    conn.close()
    return jsonify({"complexity_score": score})

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id', 'default_user')
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("SELECT complexity_score FROM user_complexity WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()
    complexity_score = score[0] if score else 1.0
    conn.close()

    # Minimal Gemini call for recommendations
    prompt = f"""
    Recommend 4 free YouTube movies (provide video IDs) based on complexity score {complexity_score} (1.0 low, 5.0 high). Include 1 each from action, comedy, thriller, horror. Use only IDs from: {json.dumps(FREE_MOVIES)}.
    """
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()['candidates'][0]['content']['parts'][0]['text']
        recommendations = json.loads(result.strip('```json\n').strip('```'))
    except Exception:
        recommendations = {"action": FREE_MOVIES["action"][0], "comedy": FREE_MOVIES["comedy"][0],
                          "thriller": FREE_MOVIES["thriller"][0], "horror": FREE_MOVIES["horror"][0]}

    return jsonify({
        "complexity_score": complexity_score,
        "recommendations": recommendations,
        "genres": FREE_MOVIES
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)