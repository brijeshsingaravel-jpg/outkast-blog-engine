import asyncio
import json
import os
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from scraper import run_scraper

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
COFOUNDER_CHAT_ID = os.environ.get("COFOUNDER_CHAT_ID")

ALL_CHAT_IDS = [TELEGRAM_CHAT_ID, COFOUNDER_CHAT_ID]

DASHBOARD_URL = "https://brijeshsingaravel-jpg.github.io/outkast-blog-engine/dashboard.html"

# --- SEND TOPIC CARDS TO BOTH ---
async def send_topic_cards(bot, topics):
    for chat_id in ALL_CHAT_IDS:
        if not chat_id:
            continue
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="😈 *Outkast Blog Engine*\nToday's trending topics are ready. First tap wins!",
                parse_mode="Markdown"
            )
            for i, t in enumerate(topics):
                text = (
                    f"🔥 *Topic {i+1}: {t['topic']}*\n\n"
                    f"📈 *Why trending:* {t['why_trending']}\n\n"
                    f"😈 *Outkast angle:* {t['outkast_angle']}\n\n"
                    f"🔑 *Keywords:* {t['keywords']}"
                )
                keyboard = [[
                    InlineKeyboardButton("✅ Write This", callback_data=f"approve_{i}"),
                    InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{i}")
                ]]
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")

# --- NOTIFY BOTH AFTER COMPLETION ---
async def send_completion_notification(bot, topic, shopify_url):
    message = (
        f"🎉 *Blog is live!*\n\n"
        f"📝 *Topic:* {topic}\n\n"
        f"🔗 *Shopify:* {shopify_url}\n\n"
        f"📊 *Content Dashboard:* {DASHBOARD_URL}\n\n"
        f"Open the dashboard to copy and schedule social posts on Metricool."
    )
    for chat_id in ALL_CHAT_IDS:
        if not chat_id:
            continue
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error notifying {chat_id}: {e}")

# --- SAVE APPROVED TOPIC ---
def save_approved_topic(topic):
    with open("approved_topic.json", "w") as f:
        json.dump(topic, f, indent=2)
    print(f"\n✅ Approved: {topic['topic']}")
    print("Saved to approved_topic.json")

# --- HANDLE BUTTON TAPS ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    topics = context.bot_data.get("topics", [])

    if context.bot_data.get("approved"):
        await query.answer("Already approved by someone else!")
        return

    await query.answer()

    if data.startswith("approve_"):
        index = int(data.split("_")[1])
        topic = topics[index]
        save_approved_topic(topic)
        context.bot_data["approved"] = True
        context.bot_data["approved_topic"] = topic

        approver_name = query.from_user.first_name or "Someone"
        approver_id = str(query.from_user.id)

        for chat_id in ALL_CHAT_IDS:
            if not chat_id:
                continue
            try:
                if str(chat_id) == approver_id:
                    await query.edit_message_text(
                        text=f"✅ *You approved:* {topic['topic']}\n\nWriting blog now... 🖊️",
                        parse_mode="Markdown"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"✅ *{approver_name} approved:* {topic['topic']}\n\nWriting blog now... 🖊️",
                        parse_mode="Markdown"
                    )
            except Exception as e:
                print(f"Error notifying approval to {chat_id}: {e}")

    elif data.startswith("skip_"):
        if not context.bot_data.get("approved"):
            index = int(data.split("_")[1])
            topic = topics[index]
            try:
                await query.edit_message_text(
                    text=f"⏭ *Skipped:* {topic['topic']}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Skip error: {e}")

# --- MAIN RUNNER ---
def run_telegram_bot(topics):
    async def main():
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        app.bot_data["topics"] = topics
        app.bot_data["approved"] = False
        app.bot_data["approved_topic"] = None
        app.add_handler(CallbackQueryHandler(handle_callback))

        await app.initialize()
        await app.start()
        await send_topic_cards(app.bot, topics)
        await app.updater.start_polling()

        print("\nWaiting for approval on Telegram (no timeout)...")

        while not app.bot_data.get("approved"):
            await asyncio.sleep(1)

        await app.updater.stop()
        await app.stop()
        await app.shutdown()

    asyncio.run(main())

# --- COMPLETION NOTIFIER ---
def notify_completion(topic, shopify_url):
    async def main():
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        async with bot:
            await send_completion_notification(bot, topic, shopify_url)
        print("✅ Completion notification sent to both.")

    asyncio.run(main())

# --- TEST RUN ---
if __name__ == "__main__":
    print("Running scraper first...")
    topics = run_scraper()
    if topics:
        print(f"\nSending {len(topics)} topic cards to Telegram...")
        run_telegram_bot(topics)
    else:
        print("No topics to send.")