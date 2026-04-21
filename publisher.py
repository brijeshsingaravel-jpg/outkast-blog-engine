import json
import os
import re
import requests
from datetime import datetime

# --- CONFIG ---
SHOPIFY_ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.environ.get("SHOPIFY_STORE_URL")

def load_generated_content():
    with open("generated_content.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- CONVERT MARKDOWN TO HTML ---
def markdown_to_html(text):
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    paragraphs = text.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<h'):
            p = f'<p>{p}</p>'
        result.append(p)
    return '\n'.join(result)

# --- EXTRACT TITLE (removes H1 from body to avoid double title) ---
def extract_title(blog_text):
    match = re.search(r'^# (.+)$', blog_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        blog_text_clean = re.sub(r'^# .+\n?', '', blog_text, count=1, flags=re.MULTILINE)
        return title, blog_text_clean
    first_line = blog_text.split('\n')[0].replace('#', '').strip()
    return first_line, blog_text

# --- EXTRACT META DESCRIPTION ---
def extract_meta(blog_text):
    if "META:" in blog_text:
        parts = blog_text.split("META:")
        meta = parts[-1].strip()[:160]
        body = parts[0].strip()
        return body, meta
    return blog_text, ""

# --- POST TO SHOPIFY BLOG ---
def post_to_shopify(content):
    blog_text = content["blog"]
    topic = content["topic"]

    title, blog_text = extract_title(blog_text)
    body, meta = extract_meta(blog_text)
    html_body = markdown_to_html(body)

    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2025-01/blogs.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    blogs_response = requests.get(url, headers=headers)
    if blogs_response.status_code != 200:
        print(f"❌ Failed to fetch blogs: {blogs_response.text}")
        return None

    blogs = blogs_response.json().get("blogs", [])
    if not blogs:
        print("❌ No blogs found on your Shopify store.")
        return None

    blog_id = blogs[0]["id"]
    print(f"✅ Found blog: {blogs[0]['title']} (ID: {blog_id})")

    article_url = f"https://{SHOPIFY_STORE_URL}/admin/api/2025-01/blogs/{blog_id}/articles.json"

    payload = {
        "article": {
            "title": title,
            "body_html": html_body,
            "summary_html": meta,
            "tags": topic,
            "published": True,
            "published_at": datetime.utcnow().isoformat() + "Z"
        }
    }

    response = requests.post(article_url, headers=headers, json=payload)

    if response.status_code == 201:
        article = response.json()["article"]
        print(f"✅ Blog posted to Shopify!")
        print(f"   Title: {article['title']}")
        print(f"   URL: https://{SHOPIFY_STORE_URL}/blogs/{blogs[0]['handle']}/{article['handle']}")
        return article
    else:
        print(f"❌ Failed to post blog: {response.text}")
        return None

# --- SAVE PUBLISH LOG ---
def save_publish_log(shopify_result):
    log = {
        "published_at": datetime.utcnow().isoformat(),
        "shopify": shopify_result["id"] if shopify_result else None,
    }
    with open("publish_log.json", "w") as f:
        json.dump(log, f, indent=2)
    print("✅ Publish log saved.")

# --- MAIN ---
if __name__ == "__main__":
    print("Loading generated content...")
    content = load_generated_content()
    print(f"Topic: {content['topic']}\n")

    print("Posting to Shopify...")
    shopify_result = post_to_shopify(content)

    if shopify_result:
        save_publish_log(shopify_result)
        print("\n🎉 Blog is live on Shopify!")
    else:
        print("\n❌ Publishing failed. Check errors above.")