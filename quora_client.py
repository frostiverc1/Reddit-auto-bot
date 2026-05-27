import json
import os
import re
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
os.makedirs("output", exist_ok=True)

QUORA_BASE = "https://www.quora.com"

# Paths that are definitely not question pages
_SKIP_PATHS = ("topic/", "profile/", "settings", "about", "login",
               "search?", "jobs", "business", "contact", "careers")


def _create_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    # Mask webdriver property to reduce bot detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def _login(driver):
    email = os.getenv("QUORA_EMAIL")
    password = os.getenv("QUORA_PASSWORD")
    if not email or not password:
        raise ValueError("QUORA_EMAIL and QUORA_PASSWORD must be set in .env")

    driver.get(QUORA_BASE)
    wait = WebDriverWait(driver, 15)

    email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    email_input.send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password + "\n")
    time.sleep(4)
    print("✅ Logged into Quora")


def _parse_score(text):
    """Convert '1.2k', '15', '2M' style strings to int."""
    text = (text or "").strip().replace(",", "")
    try:
        if text.lower().endswith("k"):
            return int(float(text[:-1]) * 1_000)
        if text.lower().endswith("m"):
            return int(float(text[:-1]) * 1_000_000)
        return int(re.search(r"\d+", text).group())
    except Exception:
        return 0


def _collect_links_from_page(driver, fetch_limit):
    """Scrape all Quora question-shaped links from the current page."""
    seen, urls = set(), []
    for a in driver.find_elements(By.TAG_NAME, "a"):
        href = (a.get_attribute("href") or "").split("?")[0].rstrip("/")
        if not href.startswith(QUORA_BASE):
            continue

        path = href[len(QUORA_BASE):].strip("/")
        if not path or any(skip in path for skip in _SKIP_PATHS):
            continue

        segments = path.split("/")
        # Accept both question-only URLs and /answer/ URLs — strip back to base question
        is_question = (
            len(segments) >= 1
            and "-" in segments[0]
            and len(segments[0]) > 5
        )
        if is_question:
            clean_url = f"{QUORA_BASE}/{segments[0]}"
            if clean_url not in seen:
                seen.add(clean_url)
                urls.append(clean_url)
                if len(urls) >= fetch_limit:
                    break

    return urls


def _get_question_links(driver, topic, fetch_limit):
    """Return up to fetch_limit question URLs, trying topic page then search fallback."""

    # ── Attempt 1: topic page ──────────────────────────────────────────────────
    driver.get(f"{QUORA_BASE}/topic/{topic}")

    # Wait until feed items with answer links are present
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/answer/']"))
        )
    except Exception:
        pass
    time.sleep(3)

    # Scroll to load more feed items
    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    urls = _collect_links_from_page(driver, fetch_limit)

    if urls:
        print(f"✅ Found {len(urls)} question URLs from topic page")
        return urls

    # ── Attempt 2: search fallback ─────────────────────────────────────────────
    print(f"⚠️  Topic page yielded nothing. Falling back to search.")
    print(f"🔄 quora.com/search?q={topic}&type=question")

    driver.get(f"{QUORA_BASE}/search?q={topic}&type=question")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/answer/']"))
        )
    except Exception:
        pass
    time.sleep(3)

    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    urls = _collect_links_from_page(driver, fetch_limit)

    if urls:
        print(f"✅ Found {len(urls)} question URLs from search page")
    else:
        print(f"❌ Search page also yielded nothing. Check credentials or try a different topic.")

    return urls


def _fetch_answer(driver, url):
    """Return a post dict (Reddit schema) for a Quora question URL."""
    driver.get(url)
    time.sleep(3)

    # Question title
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except Exception:
        title = url.split("/")[-1].replace("-", " ")

    # Wait for answer content to render
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='Answer']"))
        )
    except Exception:
        pass

    # Expand collapsed answer text ("more" / "Continue Reading")
    try:
        for btn in driver.find_elements(
            By.XPATH,
            "//button[contains(text(),'more') or contains(text(),'Continue')]"
        ):
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)
    except Exception:
        pass

    # Top answer content — ordered from most to least specific
    # Pick the longest match across all candidates to avoid grabbing UI snippets
    content = ""
    for sel in [
        ".q-box.qu-userSelect--text",
        "[class*='Answer'] .q-text",
        "[class*='answer'] .q-text",
        "[class*='Answer']",
    ]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                # Take the longest text block — most likely to be the actual answer
                candidate = max((el.text.strip() for el in els[:5]), key=len, default="")
                if len(candidate) > len(content):
                    content = candidate
        except Exception:
            continue

    # Upvote count from the upvote button label
    score = 0
    try:
        for el in driver.find_elements(
            By.XPATH,
            "//button[contains(@class,'upvote') or contains(@aria-label,'Upvote')]//span"
        ):
            text = el.text.strip()
            if text and re.search(r"\d", text):
                score = _parse_score(text)
                break
    except Exception:
        pass

    return {
        "id": url.split("/")[-1][:50],
        "title": title,
        "content": content,
        "score": score,
        "url": url,
    }


def fetch_top_posts(topic="technology", limit=10):
    """
    Fetch top questions and their top answers from a Quora topic.
    Returns a list of dicts matching the Reddit posts schema:
    { id, title, content, score, url }
    """
    driver = _create_driver()
    posts = []

    try:
        _login(driver)

        print(f"🔍 Fetching questions from topic: {topic}")
        # Fetch extra links to account for ones filtered out by quality check
        question_urls = _get_question_links(driver, topic, limit + 10)

        for url in question_urls:
            if len(posts) >= limit:
                break
            try:
                post = _fetch_answer(driver, url)
                if len(post["content"]) < 100:
                    print(f"⏭️  Skipped (content too short, {len(post['content'])} chars): {post['title'][:50]}")
                    continue
                posts.append(post)
                print(f"✅ Fetched: {post['title'][:60]}...")
            except Exception as e:
                print(f"⚠️  Skipped {url}: {e}")
    finally:
        driver.quit()

    return posts


if __name__ == "__main__":
    print("🚀 Starting Quora Client...")
    data = fetch_top_posts(topic="technology", limit=10)

    if data:
        with open("output/quora_posts.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"🎉 Successfully saved {len(data)} items to output/quora_posts.json")
    else:
        print("⚠️  No data fetched. Check your credentials and topic name.")
