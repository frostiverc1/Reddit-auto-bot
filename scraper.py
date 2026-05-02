"""

TEMPORARY FIX. 

TODO:
1. IMPLEMENT THE SAME WITH REDDIT API ONCE IT GETS APPROVED. 

"""

import requests
import json
import os
import time

os.makedirs("output", exist_ok=True)

URL = "https://www.reddit.com/r/AskReddit/top.json?t=day&limit=20"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

def fetch_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
    return None

data = fetch_data(URL)

if not data:
    print("❌ No data fetched. Exiting.")
    exit()

posts = []

for post in data["data"]["children"]:
    p = post["data"]

    content = (p.get("title", "") + "\n" + p.get("selftext", "")).strip()

    if len(content) < 100:
        continue

    if p.get("over_18"):
        continue

    posts.append({
        "id": p.get("id"),
        "title": p.get("title"),
        "content": content,
        "score": p.get("score"),
        "url": "https://reddit.com" + p.get("permalink", "")
    })

    time.sleep(0.5)  # slow down requests

with open("output/posts.json", "w") as f:
    json.dump(posts, f, indent=2)

print(f"✅ Saved {len(posts)} posts")
