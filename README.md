# Reddit Shorts Automation

This project builds an automated pipeline to transform publicly available Reddit content into short-form video scripts for storytelling and educational purposes.

---

## 📌 Overview

The pipeline processes Reddit data in stages:

Reddit → Script → (Future: Voice → Video → Upload)

---

## ⚙️ Features Implemented

### Step 1: Reddit API Client
- Fetches top posts using the Reddit API (via PRAW)
- Processes only publicly available data
- Filters high-quality content
- Saves output to output/posts.json

### Step 2: AI Script Generator
- Converts Reddit posts into short-form scripts
- Uses OpenAI API
- Saves output to output/scripts.json

---

## 📂 Project Structure

shorts-automation/

- reddit_client.py  
- script_generator.py  
- .env  
- output/  
  - posts.json  
  - scripts.json  

---

## 🔒 Compliance & Usage

- Uses the official Reddit API via PRAW  
- Operates in read-only mode  
- Does not post, comment, vote, or interact on Reddit  
- Processes only publicly available content  
- Intended for external content transformation and analysis  

---

## 🛠️ Setup

### 1. Install Dependencies

    pip install praw openai python-dotenv

### 2. Add Environment Variables

Create a .env file:

    OPENAI_API_KEY=your_api_key_here
    REDDIT_CLIENT_ID=your_client_id
    REDDIT_CLIENT_SECRET=your_client_secret
    REDDIT_USER_AGENT=your_app_name by u/yourusername

---

## ▶️ How to Run

### Step 1: Fetch Reddit Data

    python reddit_client.py

This will:
- Create output folder
- Generate posts.json

### Step 2: Generate Scripts

    python script_generator.py

This will:
- Read posts.json
- Generate scripts.json

---

## 📊 Output Format

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
        "script": "Short-form script..."
      }
    ]

---

## 🚀 Roadmap

- Text-to-Speech (TTS)
- Video generation (FFmpeg/MoviePy)
- Caption automation
- Telegram bot integration
- Full pipeline orchestration

---

## 🎯 Goal

Automate transformation of Reddit discussions into engaging multimedia content while respecting platform guidelines.