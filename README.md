# Reddit Shorts Automation (Step 1 + Step 2)

This project builds an automated pipeline to convert Reddit posts into viral YouTube Shorts scripts.

---

## 📌 What We Have Built So Far

### Step 1: Reddit Scraper (No API Version)
- Fetches top posts from Reddit using public JSON endpoint
- Filters usable content
- Saves output to output/posts.json

### Step 2: AI Script Generator
- Converts Reddit posts into short-form viral scripts
- Uses OpenAI API
- Saves output to output/scripts.json

---

## Project Structure

shorts-automation/

- scraper.py
- script_generator.py
- .env
- output/
  - posts.json
  - scripts.json

---

## Setup

### 1. Install Dependencies

pip install requests openai python-dotenv

### 2. Add Environment Variables

Create a .env file in root:

OPENAI_API_KEY=your_api_key_here

---

## How to Run

### Step 1: Run Scraper

python scraper.py

This will:
- Create output folder
- Generate posts.json

### Step 2: Generate Scripts

python script_generator.py

This will:
- Read posts.json
- Generate scripts.json

---

## Output Format

posts.json example:

[
  {
    "id": "abc123",
    "title": "...",
    "content": "...",
    "score": 1234,
    "url": "..."
  }
]

scripts.json example:

[
  {
    "id": "abc123",
    "script": "Viral short-form script..."
  }
]

---

## Notes

- Uses Reddit public JSON endpoint (no API needed)
- Filters low-quality posts
- Script quality depends on prompt tuning

---

## Next Steps

- Voice generation (TTS)
- Video creation (FFmpeg)
- Captions automation
- Telegram bot integration
- Full pipeline automation

---

## Goal

Reddit → Script → Voice → Video → Upload → Telegram Control
