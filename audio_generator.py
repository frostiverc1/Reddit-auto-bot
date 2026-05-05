import json
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("Error: ELEVENLABS_API_KEY not found in .env")
    exit()

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Ensure output directories exist
os.makedirs("output/audio", exist_ok=True)

SCRIPTS_PATH = "output/scripts.json"

if not os.path.exists(SCRIPTS_PATH):
    print("Warning: scripts.json not found. Run script_generator.py first.")
    exit()

with open(SCRIPTS_PATH, "r") as f:
    try:
        scripts = json.load(f)
    except json.JSONDecodeError:
        print("Warning: scripts.json is corrupted.")
        exit()

if not scripts:
    print("Warning: No scripts found to convert.")
    exit()

for item in scripts:
    post_id = item.get("id")
    text = item.get("script")
    
    if not post_id or not text:
        continue

    audio_path = f"output/audio/{post_id}.mp3"
    
    if os.path.exists(audio_path):
        print(f"Skipping... Audio already exists for {post_id}")
        continue

    print(f"Generating audio for {post_id}...")
    try:
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        with open(audio_path, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)
        
        print(f"Success! Saved audio for {post_id}")
    except Exception as e:
        print(f"Error generating audio for {post_id}: {e}")

print("All audio generation finished!")
