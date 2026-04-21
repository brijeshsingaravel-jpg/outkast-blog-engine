import praw
import json
import os
import requests
from groq import Groq

# --- CONFIG ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = "outkast-blog-engine/1.0"

# --- GOOGLE TRENDS (via RSS) ---
def get_google_trends():
    try:
        url = "https://trends.google.com/trending/rss?geo=IN"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        topics = []
        for item in root.findall("./channel/item"):
            title = item.find("title")
            if title is not None:
                topics.append(title.text)
        print(f"India trends: {topics[:5]}")

        url_global = "https://trends.google.com/trending/rss?geo=US"
        response_global = requests.get(url_global, headers=headers, timeout=10)
        root_global = ET.fromstring(response_global.content)
        for item in root_global.findall("./channel/item"):
            title = item.find("title")
            if title is not None:
                topics.append(title.text)

        return list(set(topics))[:20]
    except Exception as e:
        print(f"Google Trends error: {e}")
        return []

# --- REDDIT TRENDS ---
def get_reddit_trends():
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        subreddits = ["streetwear", "hiphopheads", "india", "fashion", "popculture"]
        topics = []
        for sub in subreddits:
            for post in reddit.subreddit(sub).hot(limit=5):
                topics.append(post.title)
        return topics
    except Exception as e:
        print(f"Reddit error (expected if no credentials): {e}")
        return []

# --- GROQ FILTER ---
def filter_topics_with_groq(all_topics):
    client = Groq(api_key=GROQ_API_KEY)

    topics_text = "\n".join([f"- {t}" for t in all_topics])

    prompt = f"""
You are a content strategist for Outkast — an Indian streetwear brand with a rebellious, anti-conformity identity.
The brand's universe covers: streetwear, fashion culture, music, pop culture, youth rebellion, and anything that can be given a bold counter-culture spin.

From the trending topics below, pick the 5 BEST ones that:
1. Are relevant to Outkast's universe OR can be creatively connected to it
2. Have strong blog potential (opinionated angle possible)
3. Would resonate with Indian streetwear/youth audience

For each selected topic return:
- topic: the topic name
- why_trending: one line on why it's blowing up
- outkast_angle: a sharp, rebellious Outkast POV angle for the blog
- keywords: 5 SEO keywords as a comma-separated list

Return ONLY a valid JSON array. No explanation. No markdown. Just raw JSON.

Trending topics:
{topics_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        topics = json.loads(raw)
        return topics
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {raw}")
        return []

# --- MAIN ---
def run_scraper():
    print("Fetching Google Trends...")
    google_topics = get_google_trends()
    print(f"Got {len(google_topics)} from Google Trends")

    print("Fetching Reddit trends...")
    reddit_topics = get_reddit_trends()
    print(f"Got {len(reddit_topics)} from Reddit")

    all_topics = list(set(google_topics + reddit_topics))
    print(f"Total unique topics: {len(all_topics)}")

    if not all_topics:
        print("No topics found. Check your API keys and network.")
        return []

    print("Filtering with Groq...")
    filtered = filter_topics_with_groq(all_topics)

    print(f"\n--- TOP {len(filtered)} TOPICS FOR OUTKAST ---\n")
    for i, t in enumerate(filtered, 1):
        print(f"{i}. {t['topic']}")
        print(f"   Why trending: {t['why_trending']}")
        print(f"   Outkast angle: {t['outkast_angle']}")
        print(f"   Keywords: {t['keywords']}")
        print()

    return filtered

if __name__ == "__main__":
    run_scraper()