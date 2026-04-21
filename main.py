import json
import os
from scraper import run_scraper
from telegram_bot import run_telegram_bot, notify_completion
from writer import write_content
from publisher import post_to_shopify
from dashboard_generator import save_to_log, generate_dashboard, load_log

def load_approved_topic():
    with open("approved_topic.json", "r") as f:
        return json.load(f)

def main():
    print("\n" + "="*50)
    print("😈 OUTKAST BLOG ENGINE - STARTING")
    print("="*50 + "\n")

    # STEP 1: Scrape trends
    print("STEP 1: Scraping trending topics...")
    topics = run_scraper()
    if not topics:
        print("❌ No topics found. Exiting.")
        return

    # STEP 2: Send to Telegram for approval
    print("\nSTEP 2: Sending to Telegram for approval...")
    run_telegram_bot(topics)

    # STEP 3: Load approved topic
    if not os.path.exists("approved_topic.json"):
        print("❌ No topic approved. Exiting.")
        return
    topic_data = load_approved_topic()
    print(f"\n✅ Approved topic: {topic_data['topic']}")

    # STEP 4: Write all content
    print("\nSTEP 3: Writing content with Groq...")
    content = write_content(topic_data)

    # STEP 5: Post to Shopify
    print("\nSTEP 4: Posting to Shopify...")
    shopify_result = post_to_shopify(content)
    shopify_url = ""
    if shopify_result:
        shopify_url = (
            "https://" +
            os.environ.get("SHOPIFY_STORE_URL", "") +
            "/blogs/the-outkast-journal/" +
            shopify_result["handle"]
        )
        print(f"✅ Live at: {shopify_url}")

    # STEP 6: Save to dashboard
    print("\nSTEP 5: Updating dashboard...")
    log = save_to_log(content, shopify_url)
    generate_dashboard(log)

    # STEP 7: Notify both via Telegram
    print("\nSTEP 6: Sending completion notification...")
    notify_completion(topic_data["topic"], shopify_url)

    print("\n" + "="*50)
    print("DONE! Blog is live. Dashboard updated.")
    print("Open dashboard.html to copy social content.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()