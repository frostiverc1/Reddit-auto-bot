import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Ensure output folder exists
os.makedirs("output", exist_ok=True)

POSTS_PATH = "output/posts.json"
SCRIPTS_PATH = "output/scripts.json"

# ✅ If posts.json doesn't exist, create empty one
if not os.path.exists(POSTS_PATH):
    print("⚠️ posts.json not found. Creating empty file...")
    with open(POSTS_PATH, "w") as f:
        json.dump([], f)

# ✅ Load posts safely
with open(POSTS_PATH, "r") as f:
    try:
        posts = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ posts.json is corrupted. Resetting...")
        posts = []

if not posts:
    print("⚠️ No posts found. Run scraper.py first.")
    exit()

scripts = []

def generate_script(content):
    prompt = f"""
Rewrite this Reddit post into a viral YouTube Shorts script.

Rules:
- Max 120 words
- Start with a strong hook
- Use short sentences
- Add suspense and pacing
- Make it natural
- No Reddit mentions
- End with curiosity gap

Content:
{content}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()

# ✅ Generate scripts
for post in posts:
    try:
        script = generate_script(post.get("content", ""))
        scripts.append({
            "id": post.get("id"),
            "script": script
        })
        print(f"✅ Script generated for {post.get('id')}")
    except Exception as e:
        print(f"❌ Error for {post.get('id')}: {e}")

# ✅ Save output
with open(SCRIPTS_PATH, "w") as f:
    json.dump(scripts, f, indent=2)

print("🎉 All scripts generated!")
