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
    "💼 대체투자",
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
    
    # 1. 블랙리스트 단어 검사 (포함 시 즉시 제외)
    for kw in BLACKLIST_KEYWORDS:
        if kw.lower() in text:
            return False
            
    # 2. 관심 키워드 검사 (영문은 \b 정규식, 한글은 일반 포함 검사)
    for kw in INTEREST_KEYWORDS:
        kw_lower = kw.lower()
        if re.match(r'^[a-z0-9\s-]+$', kw_lower):
            pattern = r'\b' + re.escape(kw_lower) + r'\b'
            if re.search(pattern, text):
                return True
        else:
            if kw_lower in text:
                return True
                
    return False

def get_primary_link(article: dict) -> str:
    link = article.get("link", "")
    if isinstance(link, list):
        return link[0] if link else ""
    return link

def send_aggregated_slack_news(articles) -> bool:
    """수집·분류된 기사를 4대 분야별 최대 5개씩 골라(도배 방지 적용) 슬랙으로 전송합니다."""
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL 이 설정되지 않았습니다.")
        return False

    categorized_news = {cat: [] for cat in CATEGORY_ORDER}
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 카테고리별로 분류하여 담기
    for article in articles:
        title = article.get("title", "제목 없음").strip()
        url = get_primary_link(article) or "#"
        date = article.get("date") or today_str
        category = article.get("category", "🌐 거시경제")

        formatted_item = f"• <{url}|{title} ({date})>"

        for cat_name in CATEGORY_ORDER:
            if cat_name in category or category in cat_name:
                categorized_news[cat_name].append((title.lower(), formatted_item))
                break

    message_text = "🗞️ *오늘의 주요 뉴스 브리핑*\n\n"
    has_news = False

    # 2. 특정 주제(엔비디아 등) 도배 방지 및 3~5개 선별
    for cat_name in CATEGORY_ORDER:
        items = categorized_news[cat_name]
        
        selected_items = []
        nvidia_count = 0  # 엔비디아 기사 카운터
        
        for title_lower, formatted_item in items:
            # 엔비디아 관련 기사는 카테고리당 최대 2개까지만 허용
            if "nvidia" in title_lower or "엔비디아" in title_lower:
                if nvidia_count >= 2:
                    continue
                nvidia_count += 1
                
            selected_items.append(formatted_item)
            if len(selected_items) == 5:  # 최대 5개까지만 선별
                break
        
        if len(selected_items) < 3 and len(selected_items) > 0:
            print(f"⚠️ [경고] '{cat_name}' 분야 기사가 {len(selected_items)}개로 최소 기준(3개)보다 부족합니다.")
            
        if selected_items:
            has_news = True
            message_text += f"*{cat_name}*\n"
            message_text += "\n".join(selected_items) + "\n\n"

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
    
    # [핵심 수정] 국내 VC/스타트업 RSS 기사들이 잘려나가지 않도록 수집 풀을 60개로 확대!
    merged = merged[:60]

    # --- 카테고리 분류 ---
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
