import json
import os
from groq import Groq

# --- CONFIG ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def load_approved_topic():
    with open("approved_topic.json", "r") as f:
        return json.load(f)

def load_voice_prompt():
    with open("voice_prompt.txt", "r") as f:
        return f.read().strip()

def write_content(topic_data):
    client = Groq(api_key=GROQ_API_KEY)

    topic = topic_data["topic"]
    angle = topic_data["outkast_angle"]
    keywords = topic_data["keywords"]

    voice = """
OUTKAST BRAND VOICE:
- Outkast is an Indian streetwear brand built on rebellion, anti-conformity, and raw authenticity
- Tone: Bold, opinionated, sharp, culturally aware, never corporate
- Write like a street-smart creative director who has opinions and isn't afraid to say them
- Use short punchy sentences mixed with longer ones for rhythm
- Reference Indian youth culture, street culture, music, and global trends naturally
- Never sound like a press release. Never sound generic. Never preach.
- End with a call to action that ties back to individuality and the Outkast mindset
- SEO keywords must appear naturally — never forced
"""

    # --- SHOPIFY BLOG ---
    print("Writing Shopify blog...")
    blog_prompt = f"""
{voice}

Write a full SEO blog post for Outkast's Shopify store with this brief:
Topic: {topic}
Angle: {angle}
Keywords to include naturally: {keywords}

Structure:
- Compelling H1 title (not clickbait, genuinely sharp)
- Hook intro paragraph (3-4 sentences, pull the reader in)
- 3-4 sections with H2 subheadings
- Each section 80-120 words
- Closing paragraph with Outkast brand tie-in
- Meta description (under 160 characters) at the very end labeled "META:"

Total length: 800-1000 words
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

Write a Twitter/X thread about this topic for Outkast's account:
Topic: {topic}
Angle: {angle}

Rules:
- 8 tweets maximum
- First tweet is the hook — bold, makes people stop scrolling
- Each tweet under 280 characters
- Number them: 1/ 2/ 3/ etc.
- Last tweet ties back to Outkast brand with a punch
- No hashtag spam — max 2 hashtags total in the whole thread
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

Rules:
- 150-300 words
- Conversational but sharp
- One strong opinion, backed up with 2-3 points
- End with a question to drive comments
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

Write a Reddit post for r/streetwear or r/india about this topic:
Topic: {topic}
Angle: {angle}

Rules:
- Title: genuine, curiosity-driving, not clickbait
- Body: 150-250 words
- Sound like a real person sharing an opinion, not a brand
- Subtle brand mention only at the very end, naturally
- Invite discussion with a question
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

Rules:
- Title: thoughtful, editorial style
- 500-700 words
- More reflective tone than the blog — Medium readers want depth
- 3 sections with subheadings
- End with a strong closing thought
- No direct brand promotion — let the ideas speak
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