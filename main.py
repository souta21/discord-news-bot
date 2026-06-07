import os
from pathlib import Path

import feedparser
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

RSS_URLS = [
    "https://techcrunch.com/feed/",
]

client = genai.Client(api_key=GEMINI_API_KEY)

prompt_template = Path("prompt.md").read_text(encoding="utf-8")


def summarize(title: str, description: str) -> str:
    prompt = f"""
{prompt_template}

Title:
{title}

Description:
{description}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text.strip()


def send_to_discord(message: str) -> None:
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=30,
    )

    response.raise_for_status()


def process_feed(feed_url: str) -> None:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[1]:
        title = entry.get("title", "")
        description = entry.get("summary", "")
        link = entry.get("link", "")

        summary = summarize(title, description)

        message = (
            f"📰 {title}\n\n"
            f"{summary}\n\n"
            f"{link}"
        )

        send_to_discord(message)


def main() -> None:
    for rss_url in RSS_URLS:
        process_feed(rss_url)


if __name__ == "__main__":
    main()