import praw
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure output folder exists
os.makedirs("output", exist_ok=True)

# Initialize PRAW (Official Reddit API Wrapper)
# We use a descriptive User-Agent as per Reddit's Responsible Builder Policy
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=f"python:reddit-shorts-automation:v1.0 (by /u/{os.getenv('REDDIT_USERNAME', 'unknown')})",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

def fetch_top_posts(subreddit_name="AskReddit", limit=20):
    """
    Fetches publicly available top posts from a subreddit using the official API.
    Operates in read-only mode.
    """
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Fetching top posts of the day
        for post in subreddit.top(time_filter="day", limit=limit):
            
            # Combine title and body text for processing
            content = (post.title + "\n" + post.selftext).strip()

            # Filters for high-quality content
            if len(content) < 100:
                continue
            if post.over_18:
                continue

            posts.append({
                "id": post.id,
                "title": post.title,
                "content": content,
                "score": post.score,
                "url": f"https://reddit.com{post.permalink}"
            })
            
            print(f"✅ Fetched: {post.title[:50]}...")
            
    except Exception as e:
        print(f"❌ Error fetching from Reddit API: {e}")
    
    return posts

if __name__ == "__main__":
    print("🚀 Starting Reddit API Client...")
    data = fetch_top_posts("AskReddit", limit=20)

    if data:
        with open("output/posts.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"🎉 Successfully saved {len(data)} items to output/posts.json")
    else:
        print("⚠️ No data was fetched. Please check your API credentials.")
