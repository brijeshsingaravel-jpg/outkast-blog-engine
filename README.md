# Outkast Blog Engine

A daily content pipeline for a Shopify store blog, with a human in the loop.

It runs itself at 7:00 AM IST on a GitHub Actions schedule and stops to ask before it publishes
anything.

## What it does, in order

1. **Scrapes** trending topics.
2. **Asks over Telegram.** Nothing is written or published until a person approves a topic — the
   step that makes the rest of it safe to automate.
3. **Writes** the article from the approved topic.
4. **Publishes** it to the store's blog through the Shopify Admin API.
5. **Updates a dashboard** (`dashboard.html`) and commits it back to the repo, so the log of what
   went out is in git rather than in somebody's memory.

## Running it

It runs on a schedule, and `workflow_dispatch` means you can trigger it by hand from the Actions
tab. Locally:

```bash
pip install pytrends praw groq python-telegram-bot requests google-genai
python main.py
```

There is no `requirements.txt` — the workflow installs that list directly, and this README says
the same thing rather than pointing at a file that does not exist.

## Configuration

Every credential comes from GitHub Actions secrets. **Nothing is hardcoded, and nothing belongs
in this repository:**

| Secret | What it's for |
|---|---|
| `GROQ_API_KEY` | the model that writes the article |
| `SHOPIFY_STORE_URL`, `SHOPIFY_ACCESS_TOKEN` | publishing to the store blog |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | the approval step |
| `COFOUNDER_CHAT_ID` | the second person who gets notified |

## Status

**Built for one store and still running on its schedule.** It is not a general-purpose tool and
was never meant to be — it is shared because the shape may be useful to someone building the same
thing: scrape, ask a human, generate, publish, log.

Built in Chennai.
