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
CORS(app, origins=["https://klarity-frontend.vercel.app"], supports_credentials=True)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Debug: Check if API key is loaded
print(f"GEMINI_API_KEY loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
if GEMINI_API_KEY:
    print(f"API Key length: {len(GEMINI_API_KEY)}")
else:
    print("WARNING: GEMINI_API_KEY is not set in environment variables!")

# REAL MOVIES with ACTUAL PROVIDED POSTER IMAGES + SUMMARIES
FREE_MOVIES = {
    "action": [
        {
            "id": "action_001", 
            "title": "Top Gun: Maverick", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
            "summary": "After thirty years, Maverick is still pushing the envelope as a top naval aviator, but must confront ghosts of his past when he leads TOP GUN's elite graduates on a mission that demands the ultimate sacrifice from those chosen to fly it."
        },
        {
            "id": "action_003", 
            "title": "The Dark Knight", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "summary": "Batman faces his greatest challenge yet as the Joker wreaks havoc and chaos on the people of Gotham. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to destroy organized crime in Gotham."
        },
        {
            "id": "action_004", 
            "title": "Mad Max: Fury Road", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/hA2ple9q4qnwxp3hKVNhroipsir.jpg",
            "summary": "In a post-apocalyptic wasteland, Max teams up with Furiosa to flee from cult leader Immortan Joe and his army in an armored tanker truck, leading to a high-octane road war."
        },
        {
            "id": "action_005", 
            "title": "John Wick", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg",
            "summary": "An ex-hitman comes out of retirement to track down the gangsters that took everything from him. With New York City as his bullet-riddled playground, John Wick embarks on a merciless rampage."
        },
        {
            "id": "action_006", 
            "title": "The Matrix", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "summary": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers. Neo must choose between the world he knows and the truth."
        },
        {
            "id": "action_007", 
            "title": "Gladiator", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
            "summary": "When a Roman General is betrayed and his family murdered by an emperor's corrupt son, he comes to Rome as a gladiator to seek revenge."
        },
        {
            "id": "action_008", 
            "title": "Die Hard", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/yFihWxQcmqcaBR31QM6Y8gT6aYV.jpg",
            "summary": "A New York City police officer tries to save his wife and several others taken hostage by German terrorists during a Christmas party at the Nakatomi Plaza in Los Angeles."
        }
    ],
    "comedy": [
        {
            "id": "comedy_001", 
            "title": "Deadpool", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/3E53WEZJqP6aM84D8CckXx4pIHw.jpg",
            "summary": "A fast-talking mercenary with a morbid sense of humor is subjected to a rogue experiment that leaves him with accelerated healing powers and a quest for revenge."
        },
        {
            "id": "comedy_003", 
            "title": "Superbad", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg",
            "summary": "Two co-dependent high school seniors are forced to deal with separation anxiety after their plan to stage a booze-soaked party goes awry."
        }
    ],
    "thriller": [
        {
            "id": "thriller_002", 
            "title": "Se7en", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8EngEmJskVUO.jpg",
            "summary": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives. The investigation leads them into a dark psychological game."
        },
        {
            "id": "thriller_003", 
            "title": "The Silence of the Lambs", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/rplLJ2hPcOQmkFhTqUte0MkEaO2.jpg",
            "summary": "A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims."
        },
        {
            "id": "thriller_005", 
            "title": "Shutter Island", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/4GDy0PHYX3VRXUtwK5ysFbg3kEx.jpg",
            "summary": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane. The investigation leads him to question his own sanity."
        },
        {
            "id": "thriller_006", 
            "title": "The Departed", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg",
            "summary": "An undercover cop and a police informant play a deadly game of cat and mouse with the Boston mob. Both sides struggle to uncover the identity of the other before their covers are blown."
        }
    ],
    "horror": [
        {
            "id": "horror_001", 
            "title": "The Conjuring", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/wVYREutTvI2tmxr6ujrHT704wGF.jpg",
            "summary": "Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse. They discover a malevolent entity with a disturbing past."
        },
        {
            "id": "horror_003", 
            "title": "The Exorcist", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/5x0CeVHJI8tcDx8tUUwYHQSNILq.jpg",
            "summary": "When a teenage girl is possessed by a mysterious entity, her mother seeks the help of two priests to save her daughter. The battle between good and evil begins."
        },
        {
            "id": "horror_004", 
            "title": "A Quiet Place", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg",
            "summary": "In a post-apocalyptic world, a family is forced to live in silence while hiding from monsters with ultra-sensitive hearing. They must communicate through sign language to survive."
        },
        {
            "id": "horror_006", 
            "title": "Get Out", 
            "thumbnail": "https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg",
            "summary": "A young African-American visits his white girlfriend's parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point."
        }
    ]
}

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    # Create user_complexity table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_complexity (
            user_id TEXT PRIMARY KEY,
            clicks INTEGER DEFAULT 0,
            complexity_score REAL DEFAULT 1.0
        )
    """)
    
    # Create video_cache table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_cache (
            video_id TEXT PRIMARY KEY,
            briefing TEXT,
            theme_alerts TEXT,
            recaps TEXT,
            characters TEXT,
            rating TEXT,
            complexity TEXT
        )
    """)
    
    # Add characters column to existing video_cache table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE video_cache ADD COLUMN characters TEXT")
        print("Added characters column to video_cache table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Characters column already exists in video_cache table")
        else:
            print(f"Error adding characters column: {e}")
    
    # Create movie_titles_cache table for YouTube video titles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movie_titles_cache (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create user_history table for tracking watched videos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            video_id TEXT NOT NULL,
            video_title TEXT,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_complexity(user_id)
        )
    """)
    
    # Create video_scenes table for "what just happened" answers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            scene_start INTEGER NOT NULL,
            scene_end INTEGER NOT NULL,
            what_happened TEXT NOT NULL,
            scene_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES video_cache(video_id)
        )
    """)
    
    # Create video_characters table for character information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            character_role TEXT NOT NULL,
            character_description TEXT,
            importance_level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES video_cache(video_id)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

def get_youtube_video_title(video_id):
    """Fetch video title from YouTube with caching and fallback"""
    try:
        # First check cache
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM movie_titles_cache WHERE video_id = ?", (video_id,))
        cached = cursor.fetchone()
        if cached and cached[0] and not cached[0].startswith("Movie #"):
            conn.close()
            return cached[0]
        
        # Try to fetch real title from YouTube
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"Fetching YouTube title for video: {video_id}")
            response = requests.get(youtube_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract title from HTML
                import re
                # Look for the title in the HTML - YouTube stores it in several places
                title_match = re.search(r'"title":"([^"]+)"', response.text)
                if not title_match:
                    title_match = re.search(r'<title>([^<]+)</title>', response.text)
                    if title_match:
                        title = title_match.group(1)
                        # Remove " - YouTube" suffix if present
                        title = title.replace(" - YouTube", "").strip()
                    else:
                        title = None
                else:
                    title = title_match.group(1)
                    # Decode unicode escapes
                    title = title.encode().decode('unicode_escape')
                
                if title and len(title.strip()) > 0:
                    print(f"Successfully fetched YouTube title: {title}")
                    # Cache the real title
                    cursor.execute("INSERT OR REPLACE INTO movie_titles_cache (video_id, title) VALUES (?, ?)", 
                                  (video_id, title))
                    conn.commit()
                    conn.close()
                    return title
                    
        except Exception as e:
            print(f"Error fetching YouTube title for {video_id}: {str(e)}")
        
        # Use actual titles from our curated movie database as backup
        for genre in FREE_MOVIES:
            for movie in FREE_MOVIES[genre]:
                if movie["id"] == video_id:
                    title = movie["title"]
                    # Cache the title
                    cursor.execute("INSERT OR REPLACE INTO movie_titles_cache (video_id, title) VALUES (?, ?)", 
                                  (video_id, title))
                    conn.commit()
                    conn.close()
                    return title
        
        # Final fallback for unknown videos
        title = f"Video {video_id[:8]}"
        cursor.execute("INSERT OR REPLACE INTO movie_titles_cache (video_id, title) VALUES (?, ?)", 
                      (video_id, title))
        conn.commit()
        conn.close()
        
        return title
        
    except Exception as e:
        print(f"Error in get_youtube_video_title for {video_id}: {str(e)}")
        return f"Video {video_id[:8]}"

def add_to_history(user_id, video_id, video_title):
    """Add a watched video to user's history"""
    try:
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_history (user_id, video_id, video_title)
            VALUES (?, ?, ?)
        """, (user_id, video_id, video_title))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding to history: {str(e)}")
        return False

def get_user_history(user_id):
    """Get user's watch history with thumbnails"""
    try:
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT video_id, video_title, watched_at
            FROM user_history
            WHERE user_id = ?
            ORDER BY watched_at DESC
            LIMIT 20
        """, (user_id,))
        history = cursor.fetchall()
        
        # Enhance history with thumbnails and YouTube links
        enhanced_history = []
        for row in history:
            video_id = row[0]
            title = row[1]
            watched_at = row[2]
            
            # If the title starts with "Movie #", fetch the real YouTube title
            if title and title.startswith("Movie #"):
                print(f"Refreshing title for video {video_id}: {title}")
                real_title = get_youtube_video_title(video_id)
                if real_title and not real_title.startswith("Movie #"):
                    title = real_title
                    # Update the database with the real title
                    cursor.execute("UPDATE user_history SET video_title = ? WHERE video_id = ? AND user_id = ?", 
                                  (real_title, video_id, user_id))
                    conn.commit()
                    print(f"Updated title for video {video_id}: {real_title}")
            
            # Generate YouTube thumbnail URL (high quality, fallback to medium quality)
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            enhanced_history.append({
                'video_id': video_id,
                'title': title,
                'watched_at': watched_at,
                'thumbnail': thumbnail_url,
                'youtube_url': youtube_url
            })
        
        conn.close()
        return enhanced_history
    except Exception as e:
        print(f"Error fetching history: {str(e)}")
        return []

def get_video_id(url):
    # Handle URLs without protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed_url = urlparse(url)
    
    # Handle youtu.be URLs
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    
    # Handle youtube.com URLs
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        # Standard watch URLs
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        # Embed URLs
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
    print("=== ENTERING get_gemini_response ===")
    
    # Check if API key is available
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is not set!")
        return {"error": "Gemini API key not configured"}
    
    print(f"API key available: True (length: {len(GEMINI_API_KEY)})")
    
    # Combine transcript chunks for analysis
    full_transcript = ' '.join([chunk['text'] for chunk in transcript_chunks])  # Use all chunks for better scene detection
    
    print(f"Transcript chunks processed: {len(transcript_chunks)}")
    print(f"Full transcript length: {len(full_transcript)} chars")
    print(f"Full transcript preview (first 200 chars): {full_transcript[:200]}...")
    
    # Calculate video duration from transcript chunks
    video_duration = transcript_chunks[-1]['end'] if transcript_chunks else 300  # Default to 5 minutes if no chunks
    scene_duration = max(60, video_duration // 6)  # Aim for 6 scenes, minimum 60 seconds each
    
    print(f"Video duration: {video_duration} seconds")
    print(f"Scene duration: {scene_duration} seconds")
    
    # Create scene time ranges
    scenes = []
    current_time = 0
    scene_number = 1
    
    while current_time < video_duration:
        scene_end = min(current_time + scene_duration, video_duration)
        scenes.append({
            "scene_number": scene_number,
            "start": current_time,
            "end": scene_end
        })
        current_time = scene_end
        scene_number += 1
    
    scenes_json = json.dumps(scenes, indent=2)
    print(f"Generated {len(scenes)} scenes: {scenes_json}")
    
    prompt = f"""
    Analyze this video transcript and provide a comprehensive JSON response with the following structure:
    {{
        "briefing": "A brief overview of what the video is about (2-3 sentences)",
        "characters": [
            {{
                "name": "Character Name",
                "role": "Their role or relationship to the story (e.g., 'Main protagonist', 'Love interest', 'Antagonist', 'Supporting character')",
                "description": "Brief description of the character and their importance to the story",
                "importance": 1
            }}
        ],
        "theme_alerts": [
            {{
                "timestamp": 60,
                "theme": "Theme Name",
                "emotion": "Emotion",
                "description": "Brief description"
            }}
        ],
        "recaps": [
            {{
                "timestamp_start": 0,
                "timestamp_end": 120,
                "summary": "Summary of this segment"
            }}
        ],
        "scenes": [
            {{
                "scene_start": 0,
                "scene_end": {scene_duration},
                "scene_title": "Scene Title",
                "what_happened": "A clear, concise answer to 'what just happened?' for this time period. Focus on the key events, actions, or information presented in this segment."
            }}
        ]
    }}

    IMPORTANT CHARACTER ANALYSIS: 
    - Identify the 3-6 most important characters that appear in this video
    - Focus on characters who are actively speaking, being discussed, or are central to the plot
    - For each character, provide their name (as mentioned in the transcript), their role in the story, and a brief description
    - Rate importance from 1-3 (1 = most important/main characters, 2 = important supporting characters, 3 = minor but relevant characters)
    - Only include characters that are actually relevant to understanding this video content

    SCENES: Create a "scenes" array with exactly {len(scenes)} entries covering these time ranges:
    {scenes_json}

    For each scene, provide:
    1. scene_start and scene_end (exact times from the ranges above)
    2. scene_title: A brief descriptive title for what happens in this scene
    3. what_happened: A clear, direct answer to "what just happened?" that a user would want to know if they clicked during this time period

    Transcript: {full_transcript[:4000]}
    """
    
    print(f"Prompt created (length: {len(prompt)} chars)")
    
    # Updated headers and request format for current Gemini API
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    print(f"Request headers prepared: {list(headers.keys())}")
    print(f"Request data structure: {list(data.keys())}")
    print(f"API URL: {GEMINI_API_URL}")
    
    try:
        print("Making HTTP request to Gemini API...")
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=30)
        
        print(f"HTTP response received!")
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"ERROR: Non-200 status code received")
            print(f"Response text: {response.text}")
            return {"error": f"Gemini API returned status {response.status_code}: {response.text}"}
        
        print("Parsing JSON response...")
        result = response.json()
        print("JSON parsing successful!")
        print(f"Response structure keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if 'candidates' in result:
            print(f"Found {len(result['candidates'])} candidates")
            if len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print(f"Candidate structure keys: {list(candidate.keys()) if isinstance(candidate, dict) else 'Not a dict'}")
                
                if 'content' in candidate:
                    content = candidate['content']
                    print(f"Content structure keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
                    
                    if 'parts' in content and len(content['parts']) > 0:
                        text_response = content['parts'][0]['text']
                        print(f"Text response extracted successfully!")
                        print(f"Response length: {len(text_response)} chars")
                        print(f"Response preview (first 300 chars): {text_response[:300]}...")
                        print("=== get_gemini_response SUCCESS ===")
                        return text_response
                    else:
                        print(f"ERROR: No parts in content or parts is empty")
                        print(f"Content structure: {content}")
                        return {"error": f"No parts in content: {content}"}
                else:
                    print(f"ERROR: No content in candidate")
                    print(f"Candidate structure: {candidate}")
                    return {"error": f"No content in candidate: {candidate}"}
            else:
                print("ERROR: No candidates found in response")
                return {"error": "No candidates in response"}
        else:
            print("ERROR: No candidates key in response")
            print(f"Full response: {result}")
            return {"error": f"No candidates key in response: {result}"}
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
        return {"error": "Gemini API request timed out"}
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection error")
        return {"error": "Failed to connect to Gemini API"}
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON decode error: {e}")
        print(f"Response text: {response.text}")
        return {"error": f"JSON decode error: {e}"}
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        print(f"Error type: {type(e)}")
        return {"error": f"Gemini API error: {str(e)}"}
    
    print("=== get_gemini_response END (shouldn't reach here) ===")
    return {"error": "Unexpected end of function"}

def update_complexity_score(user_id, click_count):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_complexity (user_id, clicks, complexity_score) VALUES (?, ?, ?)",
                   (user_id, click_count, max(1.0, 5.0 - (click_count * 0.1))))
    conn.commit()
    conn.close()

@app.route('/process_video', methods=['POST'])
def process_video():
    conn = None
    try:
        print("=== STARTING VIDEO PROCESSING ===")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        
        # Validate request data
        data = request.get_json()
        print(f"Received JSON data: {data}")
        
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({"error": "Invalid JSON data"}), 400
            
        youtube_url = data.get('youtube_url')
        user_id = data.get('user_id', 'default_user')
        
        print(f"Processing video URL: '{youtube_url}'")
        print(f"URL type: {type(youtube_url)}")
        print(f"URL length: {len(youtube_url) if youtube_url else 'None'}")
        print(f"User ID: {user_id}")
        
        if not youtube_url:
            print("ERROR: No YouTube URL provided")
            return jsonify({"error": "No YouTube URL provided"}), 400

        # Test URL parsing with detailed debugging
        print(f"Testing URL parsing for: {youtube_url}")
        video_id = get_video_id(youtube_url)
        print(f"Extracted video ID: {video_id}")
        
        if not video_id:
            print("ERROR: Invalid YouTube URL - get_video_id returned None")
            # Let's also test the URL parsing step by step
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(youtube_url)
            print(f"Parsed URL hostname: {parsed_url.hostname}")
            print(f"Parsed URL path: {parsed_url.path}")
            print(f"Parsed URL query: {parsed_url.query}")
            return jsonify({"error": "Invalid YouTube URL. Please use a valid YouTube URL like: https://www.youtube.com/watch?v=VIDEO_ID"}), 400

        print(f"Successfully extracted video ID: {video_id}")

        # Initialize database connection
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        
        # Check cache
        print("Checking cache for video...")
        cursor.execute("SELECT briefing, theme_alerts, recaps, characters FROM video_cache WHERE video_id = ?", (video_id,))
        cached = cursor.fetchone()
        if cached:
            print("Found cached data, returning cached response")
            try:
                result = {
                    "briefing": cached[0],
                    "theme_alerts": json.loads(cached[1]) if cached[1] else [],
                    "recaps": json.loads(cached[2]) if cached[2] else [],
                    "characters": json.loads(cached[3]) if cached[3] else []
                }
                
                # Add to history
                video_title = get_youtube_video_title(video_id)
                add_to_history(user_id, video_id, video_title)
                
                return jsonify(result)
            except Exception as e:
                print(f"Error parsing cached data: {e}")
                # Continue to process video if cache is corrupted
        
        # Get user complexity score
        cursor.execute("SELECT complexity_score FROM user_complexity WHERE user_id = ?", (user_id,))
        score = cursor.fetchone()
        complexity_score = score[0] if score else 1.0
        
        print(f"User complexity score: {complexity_score}")
        
        # Fetch transcript
        print("Fetching transcript...")
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            print(f"Transcript fetched successfully. {len(transcript_list)} entries")
        except TranscriptsDisabled:
            print("ERROR: Transcripts disabled for this video")
            return jsonify({"error": "Transcripts are disabled for this video"}), 400
        except NoTranscriptFound:
            print("ERROR: No transcript found")
            return jsonify({"error": "No transcript found for this video"}), 400
        except Exception as e:
            print(f"ERROR: Transcript fetch failed: {e}")
            return jsonify({"error": f"Failed to fetch transcript: {str(e)}"}), 400
        
        # Process transcript
        print("Processing transcript...")
        chunked_transcript = chunk_transcript(transcript_list)
        print(f"Transcript chunked into {len(chunked_transcript)} chunks")
        
        # Call Gemini API
        print("Calling Gemini API...")
        gemini_response = get_gemini_response(chunked_transcript, complexity_score)
        
        if isinstance(gemini_response, dict) and 'error' in gemini_response:
            print(f"ERROR: Gemini API call failed: {gemini_response['error']}")
            return jsonify(gemini_response), 500
        
        print("Gemini API call successful")
        
        # Cache the response
        print("Caching response...")
        cursor.execute("""
            INSERT OR REPLACE INTO video_cache 
            (video_id, briefing, theme_alerts, recaps, characters, rating, complexity) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            gemini_response.get('briefing', ''),
            json.dumps(gemini_response.get('theme_alerts', [])),
            json.dumps(gemini_response.get('recaps', [])),
            json.dumps(gemini_response.get('characters', [])),
            gemini_response.get('rating', ''),
            gemini_response.get('complexity', '')
        ))
        
        conn.commit()
        print("Response cached successfully")
        
        # Add to history
        video_title = get_youtube_video_title(video_id)
        add_to_history(user_id, video_id, video_title)
        
        return jsonify(gemini_response)
        
    except Exception as e:
        print(f"CRITICAL ERROR in process_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

@app.route('/update_clicks', methods=['POST'])
def update_clicks():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        user_id = data.get('user_id', 'default_user')
        click_count = data.get('clicks', 0)
        
        # Validate click count
        if not isinstance(click_count, int) or click_count < 0:
            return jsonify({"error": "Invalid click count"}), 400
            
        update_complexity_score(user_id, click_count)
        
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        cursor.execute("SELECT complexity_score FROM user_complexity WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result:
            score = result[0]
        else:
            # Fallback if user not found
            score = 1.0
            
        conn.close()
        return jsonify({"complexity_score": score})
        
    except Exception as e:
        print(f"Error in update_clicks: {str(e)}")
        return jsonify({"error": "Internal server error", "complexity_score": 1.0}), 500

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        cursor.execute("SELECT complexity_score FROM user_complexity WHERE user_id = ?", (user_id,))
        score = cursor.fetchone()
        complexity_score = score[0] if score else 1.0
        conn.close()

        # Use simple algorithm for recommendations based on complexity score
        # Higher complexity = more complex movies (later in the list)
        try:
            index = min(int(complexity_score) - 1, len(FREE_MOVIES["action"]) - 1)
            index = max(0, index)  # Ensure index is not negative
            
            recommendations = {
                "action": FREE_MOVIES["action"][index],
                "comedy": FREE_MOVIES["comedy"][index],
                "thriller": FREE_MOVIES["thriller"][index],
                "horror": FREE_MOVIES["horror"][index]
            }
        except Exception as e:
            print(f"Error creating recommendations: {str(e)}")
            recommendations = {
                "action": FREE_MOVIES["action"][0], 
                "comedy": FREE_MOVIES["comedy"][0],
                "thriller": FREE_MOVIES["thriller"][0], 
                "horror": FREE_MOVIES["horror"][0]
            }

        # Return all movies for browsing by genre (Netflix-style)
        genres_expanded = {}
        for genre, movies in FREE_MOVIES.items():
            # Get different movies than recommendation to avoid duplicates
            rec_id = recommendations[genre]["id"] if genre in recommendations else None
            available_movies = [m for m in movies if m["id"] != rec_id]
            if available_movies:
                genres_expanded[genre] = available_movies  # All movies except the recommended one
            else:
                genres_expanded[genre] = movies[1:]  # Skip first movie if it's the recommended one

        return jsonify({
            "complexity_score": complexity_score,
            "recommendations": recommendations,
            "genres": genres_expanded
        })
        
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "complexity_score": 1.0,
            "recommendations": {
                "action": FREE_MOVIES["action"][0],
                "comedy": FREE_MOVIES["comedy"][0], 
                "thriller": FREE_MOVIES["thriller"][0],
                "horror": FREE_MOVIES["horror"][0]
            },
            "genres": {genre: [movies[0]] for genre, movies in FREE_MOVIES.items()}
        }), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    try:
        user_id = request.args.get('user_id', 'default_user')
        history = get_user_history(user_id)
        
        return jsonify({
            "history": history
        })
        
    except Exception as e:
        print(f"Error in get_history: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "history": []
        }), 500

@app.route('/get_movie_details/<movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get detailed information about a specific movie"""
    try:
        # Search for the movie in all genres
        for genre in FREE_MOVIES:
            for movie in FREE_MOVIES[genre]:
                if movie["id"] == movie_id:
                    return jsonify({
                        "movie": movie,
                        "genre": genre,
                        "status": "success"
                    })
        
        # Movie not found
        return jsonify({
            "error": "Movie not found",
            "status": "error"
        }), 404
        
    except Exception as e:
        print(f"Error getting movie details: {str(e)}")
        return jsonify({
            "error": "Failed to get movie details",
            "status": "error"
        }), 500

@app.route('/test_gemini', methods=['POST'])
def test_gemini():
    """Test endpoint to verify Gemini API is working"""
    try:
        print("=== TESTING GEMINI API DIRECTLY ===")
        
        # Create a simple test transcript
        test_transcript_chunks = [
            {
                'start': 0,
                'end': 30,
                'text': 'Hello everyone, welcome to this video about cooking pasta. Today we will learn how to make a delicious spaghetti dish.'
            },
            {
                'start': 30,
                'end': 60,
                'text': 'First, we need to boil water in a large pot. Add some salt to the water for better flavor.'
            },
            {
                'start': 60,
                'end': 90,
                'text': 'While the water is heating, we can prepare our sauce with tomatoes, garlic, and herbs.'
            }
        ]
        
        print(f"Test transcript created with {len(test_transcript_chunks)} chunks")
        
        # Call Gemini API with test data
        response = get_gemini_response(test_transcript_chunks, 1.0)
        
        print(f"Test response received, type: {type(response)}")
        
        if isinstance(response, dict) and 'error' in response:
            return jsonify({
                "success": False,
                "error": response['error'],
                "message": "Gemini API test failed"
            })
        
        return jsonify({
            "success": True,
            "response": response,
            "message": "Gemini API test successful"
        })
        
    except Exception as e:
        print(f"Error in test_gemini: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Test endpoint failed"
        })

@app.route('/debug_config', methods=['GET'])
def debug_config():
    """Debug endpoint to check configuration"""
    try:
        return jsonify({
            "gemini_api_key_present": bool(GEMINI_API_KEY),
            "gemini_api_key_length": len(GEMINI_API_KEY) if GEMINI_API_KEY else 0,
            "gemini_api_url": GEMINI_API_URL,
            "env_file_check": os.path.exists('.env'),
            "current_directory": os.getcwd()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Debug endpoint failed"
        })

@app.route('/get_characters', methods=['GET'])
def get_characters():
    """Get character information for a specific video"""
    try:
        video_id = request.args.get('video_id')
        
        if not video_id:
            return jsonify({"error": "video_id is required"}), 400
        
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT character_name, character_role, character_description, importance_level
            FROM video_characters
            WHERE video_id = ?
            ORDER BY importance_level ASC, character_name ASC
        """, (video_id,))
        
        characters = cursor.fetchall()
        conn.close()
        
        character_list = []
        for row in characters:
            character_list.append({
                "name": row[0],
                "role": row[1],
                "description": row[2],
                "importance": row[3]
            })
        
        return jsonify({
            "success": True,
            "characters": character_list
        })
    
    except Exception as e:
        print(f"Error in get_characters: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "characters": []
        })

@app.route('/what_happened', methods=['POST'])
def what_happened():
    """Get 'what just happened' answer for a specific timestamp"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        video_id = data.get('video_id')
        timestamp = data.get('timestamp')  # Current video timestamp in seconds
        
        if not video_id or timestamp is None:
            return jsonify({"error": "video_id and timestamp are required"}), 400
        
        print(f"Looking for 'what happened' at timestamp {timestamp} for video {video_id}")
        
        # Find the scene that contains this timestamp
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scene_start, scene_end, scene_title, what_happened
            FROM video_scenes
            WHERE video_id = ? AND scene_start <= ? AND scene_end > ?
            ORDER BY scene_start
            LIMIT 1
        """, (video_id, timestamp, timestamp))
        
        scene = cursor.fetchone()
        conn.close()
        
        if scene:
            return jsonify({
                "success": True,
                "scene_start": scene[0],
                "scene_end": scene[1],
                "scene_title": scene[2],
                "what_happened": scene[3],
                "timestamp": timestamp
            })
        else:
            # If no scene found, return a generic response
            return jsonify({
                "success": False,
                "error": "No scene data found for this timestamp",
                "timestamp": timestamp,
                "what_happened": "Scene information is not available for this moment in the video."
            })
    
    except Exception as e:
        print(f"Error in what_happened: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "what_happened": "Unable to retrieve scene information at this time."
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)