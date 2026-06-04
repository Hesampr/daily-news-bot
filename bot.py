import os

from fetchers import hackernews, rss_feeds
from processor.deduplicator import deduplicate_and_merge
from processor.summarizer import summarize
from bot.telegram_sender import send_message, format_article, send_error_report
from config import (
    INTEREST_KEYWORDS,
    BLACKLIST_KEYWORDS,
    HN_KEYWORDS,
    RSS_SOURCES,
    MAX_ARTICLES_PER_RUN,
)

SEEN_FILE = "seen_news.txt"


def load_seen() -> set:
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(seen: set) -> None:
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(seen))


def is_relevant(article: dict) -> bool:
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    for kw in BLACKLIST_KEYWORDS:
        if kw.lower() in text:
            return False
    for kw in INTEREST_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def get_primary_link(article: dict) -> str:
    link = article.get("link", "")
    if isinstance(link, list):
        return link[0] if link else ""
    return link


def main():
    seen = load_seen()
    all_errors = []
    failed_sources = []
    succeeded_sources = []
    all_articles = []

    # --- Hacker News ---
    hn_articles, hn_errors = hackernews.fetch(HN_KEYWORDS)
    if hn_errors:
        failed_sources.append("Hacker News")
        all_errors.extend(hn_errors)
    else:
        succeeded_sources.append("Hacker News")
    all_articles.extend(hn_articles)

    # --- RSS Feeds ---
    rss_articles, rss_errors = rss_feeds.fetch()
    rss_failed_names = {e.split(":")[0].strip() for e in rss_errors}
    rss_succeeded_names = set(RSS_SOURCES.keys()) - rss_failed_names
    failed_sources.extend(list(rss_failed_names))
    succeeded_sources.extend(list(rss_succeeded_names))
    all_errors.extend(rss_errors)
    all_articles.extend(rss_articles)

    total_sources = len(succeeded_sources) + len(failed_sources)

    # --- Filter ---
    skipped = 0
    filtered = []
    for article in all_articles:
        link = get_primary_link(article)
        if not link or not article.get("title"):
            skipped += 1
            continue
        if link in seen:
            continue
        if not is_relevant(article):
            continue
        filtered.append(article)

    # --- Deduplicate & Merge ---
    merged, dedup_errors = deduplicate_and_merge(filtered)
    all_errors.extend(dedup_errors)
    merged = merged[:MAX_ARTICLES_PER_RUN]

    # --- Summarize & Send ---
    no_summary = 0
    articles_sent = 0

    for article in merged:
        article, sum_errors = summarize(article)
        if sum_errors:
            no_summary += 1
            all_errors.extend(sum_errors)

        message = format_article(article)
        success = send_message(message)

        if success:
            articles_sent += 1
            links = article.get("link", [])
            if isinstance(links, list):
                seen.update(links)
            else:
                seen.add(links)

    # --- Save & Report ---
    save_seen(seen)

    report = {
        "total_sources": total_sources,
        "succeeded_sources": len(succeeded_sources),
        "failed_sources": failed_sources,
        "skipped_articles": skipped,
        "no_summary": no_summary,
        "articles_sent": articles_sent,
    }
    # send_error_report(report)


if __name__ == "__main__":
    main()