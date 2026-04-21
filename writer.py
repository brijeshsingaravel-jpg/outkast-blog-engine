import json
import os
from groq import Groq

# --- CONFIG ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def load_approved_topic():
    with open("approved_topic.json", "r") as f:
        return json.load(f)

def load_voice_prompt():
    with open("voice_prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def write_content(topic_data):
    client = Groq(api_key=GROQ_API_KEY)
    voice = load_voice_prompt()

    topic = topic_data["topic"]
    angle = topic_data["outkast_angle"]
    keywords = topic_data["keywords"]

    # --- SHOPIFY BLOG ---
    print("Writing Shopify blog...")
    blog_prompt = f"""
{voice}

Write a full SEO blog post for Outkast's Shopify store with this brief:
Topic: {topic}
Angle: {angle}
Keywords to include naturally: {keywords}

Structure:
- Compelling H1 title (sharp, unexpected — not clickbait)
- Hook intro paragraph (2-3 sentences, pull the reader in immediately)
- 3-4 sections with sharp H2 subheadings
- Each section 80-120 words
- Closing paragraph tying back to Outkast's world
- Meta description under 160 characters at the very end labeled "META:"

Total length: 800-1000 words
Follow the voice, structure, and rules exactly as defined above.
"""
    blog_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": blog_prompt}],
        temperature=0.8
    )
    blog_content = blog_response.choices[0].message.content.strip()

    # --- TWITTER THREAD ---
    print("Writing Twitter thread...")
    twitter_prompt = f"""
{voice}

Write a Twitter/X thread for Outkast's account:
Topic: {topic}
Angle: {angle}

Follow the TWITTER THREAD STYLE rules defined above exactly.
- 8 tweets maximum
- Number them: 1/ 2/ 3/ etc.
- Each tweet under 280 characters
- Max 2 hashtags in the entire thread
"""
    twitter_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": twitter_prompt}],
        temperature=0.8
    )
    twitter_content = twitter_response.choices[0].message.content.strip()

    # --- THREADS POST ---
    print("Writing Threads post...")
    threads_prompt = f"""
{voice}

Write a single Threads post for Outkast's account:
Topic: {topic}
Angle: {angle}

Follow the THREADS STYLE rules defined above exactly.
- 150-300 words
- One strong opinion, 2-3 supporting points
- End with a question
- No hashtags
"""
    threads_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": threads_prompt}],
        temperature=0.8
    )
    threads_content = threads_response.choices[0].message.content.strip()

    # --- REDDIT POST ---
    print("Writing Reddit post...")
    reddit_prompt = f"""
{voice}

Write a Reddit post about this topic:
Topic: {topic}
Angle: {angle}

Follow the REDDIT STYLE rules defined above exactly.
- Title: genuine, curiosity-driving
- Body: 150-250 words
- Sound like a real person, not a brand
- Subtle brand mention only if completely natural at the end
- End with a question to invite discussion
"""
    reddit_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": reddit_prompt}],
        temperature=0.8
    )
    reddit_content = reddit_response.choices[0].message.content.strip()

    # --- MEDIUM ARTICLE ---
    print("Writing Medium article...")
    medium_prompt = f"""
{voice}

Write a Medium article about this topic:
Topic: {topic}
Angle: {angle}
Keywords: {keywords}

Follow the MEDIUM STYLE rules defined above exactly.
- Title: thoughtful, editorial style
- 500-700 words
- 3 sections with sharp subheadings
- More reflective tone — let the ideas breathe
- Strong closing thought
- No direct brand promotion
"""
    medium_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": medium_prompt}],
        temperature=0.8
    )
    medium_content = medium_response.choices[0].message.content.strip()

    # --- SAVE ALL OUTPUT ---
    output = {
        "topic": topic,
        "keywords": keywords,
        "blog": blog_content,
        "twitter": twitter_content,
        "threads": threads_content,
        "reddit": reddit_content,
        "medium": medium_content
    }

    with open("generated_content.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n✅ All content generated and saved to generated_content.json")
    return output

def preview_content(output):
    print("\n" + "="*60)
    print("SHOPIFY BLOG PREVIEW")
    print("="*60)
    print(output["blog"][:500] + "...\n")

    print("="*60)
    print("TWITTER THREAD PREVIEW")
    print("="*60)
    print(output["twitter"][:300] + "...\n")

    print("="*60)
    print("THREADS POST PREVIEW")
    print("="*60)
    print(output["threads"][:300] + "...\n")

if __name__ == "__main__":
    print("Loading approved topic...")
    topic_data = load_approved_topic()
    print(f"Topic: {topic_data['topic']}\n")

    output = write_content(topic_data)
    preview_content(output)