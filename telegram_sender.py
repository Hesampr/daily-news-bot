import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def _post(text: str) -> bool:
    try:
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        return response.status_code == 200
    except Exception:
        return False


def send_message(text: str) -> bool:
    success = _post(text)
    if not success:
        # Retry once
        success = _post(text)
    return success


def format_article(article: dict) -> str:
    title = article.get("title", "No title")
    field = article.get("field", "General Tech")
    tags = ", ".join(article.get("tags", [])) or "N/A"
    date = article.get("date", "Unknown date")
    summary = article.get("summary", "Summary unavailable")

    sources = article.get("source", [])
    links = article.get("link", [])
    if isinstance(sources, str):
        sources = [sources]
    if isinstance(links, str):
        links = [links]

    source_parts = []
    for i, src in enumerate(sources):
        link = links[i] if i < len(links) else "#"
        source_parts.append(f'<a href="{link}">{src}</a>')
    sources_text = " | ".join(source_parts)

    return (
        f"📌 <b>{title}</b>\n\n"
        f"🗂 <b>Field:</b> {field}\n"
        f"🏷 <b>Tags:</b> {tags}\n"
        f"📅 <b>Date:</b> {date}\n\n"
        f"📝 <b>Summary:</b>\n{summary}\n\n"
        f"🔗 <b>Sources:</b> {sources_text}"
    )


def send_error_report(report: dict) -> None:
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    total = report.get("total_sources", 0)
    succeeded = report.get("succeeded_sources", 0)
    failed = report.get("failed_sources", [])
    skipped = report.get("skipped_articles", 0)
    no_summary = report.get("no_summary", 0)
    sent = report.get("articles_sent", 0)

    failed_list = "\n".join([f"  • {s}" for s in failed]) if failed else "  None"

    text = (
        f"🔧 <b>Daily Run Report — {date_str}</b>\n\n"
        f"✅ Sources succeeded: {succeeded}/{total}\n"
        f"❌ Failed sources:\n{failed_list}\n\n"
        f"⚠️ Articles skipped (missing fields): {skipped}\n"
        f"⚠️ Summaries unavailable: {no_summary}\n"
        f"📨 Articles sent: {sent}"
    )

    send_message(text)
