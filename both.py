import os
import requests
from datetime import datetime

from fetchers import hackernews, rss_feeds
from processor.deduplicator import deduplicate_and_merge
from processor.summarizer import summarize, keyword_hit
from config import (
    INTEREST_KEYWORDS,
    BLACKLIST_KEYWORDS,
    HN_KEYWORDS,
    CATEGORIES,
    MAX_PER_CATEGORY,
    OVERSEAS_PREFERRED_DOMAINS,
    REGION_WEIGHT,
    source_region,
)

SEEN_FILE = "seen_news.txt"
CATEGORY_ORDER = list(CATEGORIES.keys())     # ✅ config에서 동적으로 (하드코딩 제거)
MIN_PER_CATEGORY_WARN = 3


def load_seen() -> set:
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(seen: set) -> None:
    # 무한 증가 방지: 최근 5000개만 유지
    trimmed = list(seen)[-5000:]
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(trimmed))


def is_relevant(article: dict) -> bool:
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    for kw in BLACKLIST_KEYWORDS:
        if keyword_hit(kw, text):
            return False
    for kw in INTEREST_KEYWORDS:
        if keyword_hit(kw, text):
            return True
    return False


def get_primary_link(article: dict) -> str:
    link = article.get("link", "")
    if isinstance(link, list):
        return link[0] if link else ""
    return link


def _article_region(article: dict) -> str:
    src = article.get("source")
    names = src if isinstance(src, list) else [src]
    return "global" if any(source_region(n) == "global" for n in names if n) else "kr"


def _selection_score(article: dict, category: str) -> float:
    """relevance 기반 + 해외선호 도메인에서 global 소스 가점."""
    score = float(article.get("relevance", 0))
    if category in OVERSEAS_PREFERRED_DOMAINS and _article_region(article) == "global":
        score *= REGION_WEIGHT.get("global", 1.0)
    return score


def send_aggregated_slack_news(articles) -> bool:
    """카테고리별로 relevance(+해외가점) 상위 MAX_PER_CATEGORY개를 골라 슬랙 1회 전송."""
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL 이 설정되지 않았습니다.")
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")
    buckets = {cat: [] for cat in CATEGORY_ORDER}
    for a in articles:
        cat = a.get("category", CATEGORY_ORDER[-1])
        if cat not in buckets:
            cat = CATEGORY_ORDER[-1]
        buckets[cat].append(a)

    message_text = "🗞️ *오늘의 주요 뉴스 브리핑*\n\n"
    has_news = False

    for cat_name in CATEGORY_ORDER:
        ranked = sorted(buckets[cat_name],
                        key=lambda a: _selection_score(a, cat_name),
                        reverse=True)

        selected = []
        nvidia_count = 0
        for a in ranked:
            title_lower = a.get("title", "").lower()
            if "nvidia" in title_lower or "엔비디아" in title_lower:
                if nvidia_count >= 2:      # 특정 주제 도배 방지
                    continue
                nvidia_count += 1
            selected.append(a)
            if len(selected) >= MAX_PER_CATEGORY:
                break

        if 0 < len(selected) < MIN_PER_CATEGORY_WARN:
            print(f"⚠️ [경고] '{cat_name}' 기사 {len(selected)}개 — 최소 {MIN_PER_CATEGORY_WARN}개 미만.")

        if selected:
            has_news = True
            message_text += f"*{cat_name}*\n"
            for a in selected:
                title = a.get("title", "제목 없음").strip()
                url = get_primary_link(a) or "#"
                date = a.get("date") or today_str
                message_text += f"• <{url}|{title} ({date})>\n"
            message_text += "\n"

    if not has_news:
        message_text += "오늘 조건에 맞는 새로운 뉴스가 없습니다."

    response = requests.post(slack_webhook_url, json={"text": message_text})
    if response.status_code == 200:
        print("슬랙 메시지 통합 전송 성공!")
        return True
    print(f"슬랙 전송 실패: {response.status_code}, {response.text}")
    return False


def main():
    seen = load_seen()
    all_errors = []
    all_articles = []

    hn_articles, hn_errors = hackernews.fetch(HN_KEYWORDS)
    all_errors.extend(hn_errors)
    all_articles.extend(hn_articles)

    rss_articles, rss_errors = rss_feeds.fetch()
    all_errors.extend(rss_errors)
    all_articles.extend(rss_articles)

    # --- 키워드/중복(seen) 필터 ---
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

    # --- 분류 + relevance 점수 부여 ---
    classified = []
    for article in merged:
        article, sum_errors = summarize(article)
        all_errors.extend(sum_errors)
        classified.append(article)

    # 카테고리별로 각자 top-N을 뽑으므로 전역 truncation은 하지 않는다.
    # (전역 컷을 하면 relevance 낮은 카테고리(예: 국어 매크로)가 통째로 굶는다.)
    classified.sort(key=lambda a: a.get("relevance", 0), reverse=True)

    if classified:
        success = send_aggregated_slack_news(classified)
        if success:
            for article in classified:
                links = article.get("link", [])
                if isinstance(links, list):
                    seen.update(links)
                else:
                    seen.add(links)
    else:
        print("전송할 새로운 기사가 없습니다.")

    save_seen(seen)

    # --- 수집 오류 리포트(깃헙 액션 로그) ---
    if all_errors:
        print(f"\n⚠️ 수집 오류 {len(all_errors)}건:")
        for e in all_errors:
            print(f"  • {e}")


if __name__ == "__main__":
    main()
