import requests

url = "https://www.reddit.com/r/AskReddit/top.json?t=day&limit=10"
headers = {"User-Agent": "Mozilla/5.0"}

data = requests.get(url, headers=headers).json()

for post in data["data"]["children"]:
    print(post["data"]["title"])