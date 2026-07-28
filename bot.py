import os
import re
import requests
from datetime import datetime
from fetchers import hackernews, rss_feeds
from processor.deduplicator import deduplicate_and_merge
from processor.summarizer import summarize
from config import (
    INTEREST_KEYWORDS,
    BLACKLIST_KEYWORDS,
    HN_KEYWORDS,
    RSS_SOURCES,
    MAX_ARTICLES_PER_RUN,
)

SEEN_FILE = "seen_news.txt"
CATEGORY_ORDER = [
    "🌱 임팩트",
    "🤖 AI",
    "💼 대체투자 (PE, VC, AC)",
    "🌐 거시경제"
]

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
    
    # 1. 블랙리스트 단어는 기존처럼 포함만 되어도 바로 제외
    for kw in BLACKLIST_KEYWORDS:
        if kw.lower() in text:
            return False
            
    # 2. 관심 키워드는 단어 앞뒤에 경계(\b)가 있는 '독립된 단어'일 때만 통과
    for kw in INTEREST_KEYWORDS:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text):
            return True
            
    return False

def get_primary_link(article: dict) -> str:
    link = article.get("link", "")
    if isinstance(link, list):
        return link[0] if link else ""
    return link

def send_aggregated_slack_news(articles) -> bool:
    """수집·분류된 기사를 단 1개의 슬랙 메시지로 통합 전송합니다."""
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL 이 설정되지 않았습니다.")
        return False

    categorized_news = {cat: [] for cat in CATEGORY_ORDER}
    today_str = datetime.now().strftime("%Y-%m-%d")

    for article in articles:
        title = article.get("title", "제목 없음").strip()
        url = get_primary_link(article) or "#"
        date = article.get("date") or today_str
        category = article.get("category", "🌐 거시경제")

        formatted_item = f"• <{url}|{title} ({date})>"

        for cat_name in CATEGORY_ORDER:
            if cat_name in category or category in cat_name:
                if len(categorized_news[cat_name]) < 5:
                    categorized_news[cat_name].append(formatted_item)
                break

    message_text = "🗞️ *오늘의 주요 뉴스 브리핑*\n\n"
    has_news = False

    for cat_name in CATEGORY_ORDER:
        items = categorized_news[cat_name]
        if items:
            has_news = True
            message_text += f"*{cat_name}*\n"
            message_text += "\n".join(items) + "\n\n"

    if not has_news:
        message_text += "오늘 조건에 맞는 새로운 뉴스가 없습니다."

    response = requests.post(slack_webhook_url, json={"text": message_text})
    if response.status_code == 200:
        print("슬랙 메시지 통합 전송 성공!")
        return True
    else:
        print(f"슬랙 전송 실패: {response.status_code}, {response.text}")
        return False

def main():
    seen = load_seen()
    all_errors = []
    all_articles = []

    # --- Hacker News 수집 ---
    hn_articles, hn_errors = hackernews.fetch(HN_KEYWORDS)
    if hn_errors:
        all_errors.extend(hn_errors)
    else:
        all_articles.extend(hn_articles)

    # --- RSS Feeds 수집 ---
    rss_articles, rss_errors = rss_feeds.fetch()
    all_errors.extend(rss_errors)
    all_articles.extend(rss_articles)

    # --- 키워드 및 중복 필터링 ---
    filtered = []
    for article in all_articles:
        link = get_primary_link(article)
        if not link or not article.get("title"):
            continue
        if link in seen:
            continue
        if not is_relevant(article):
            continue
        filtered.append(article)

    # --- 유사 기사 병합 ---
    merged, dedup_errors = deduplicate_and_merge(filtered)
    all_errors.extend(dedup_errors)
    merged = merged[:MAX_ARTICLES_PER_RUN]

    # --- AI 카테고리 분류 ---
    classified_articles = []
    for article in merged:
        article, sum_errors = summarize(article)
        if sum_errors:
            all_errors.extend(sum_errors)
        classified_articles.append(article)

    # --- 슬랙 1회 통합 발송 ---
    if classified_articles:
        success = send_aggregated_slack_news(classified_articles)
        if success:
            for article in classified_articles:
                links = article.get("link", [])
                if isinstance(links, list):
                    seen.update(links)
                else:
                    seen.add(links)
    else:
        print("전송할 새로운 기사가 없습니다.")

    # --- 본 기사 목록 저장 ---
    save_seen(seen)

if __name__ == "__main__":
    main()
