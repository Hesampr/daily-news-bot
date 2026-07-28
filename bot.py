import os
import re
import urllib.parse
import base64
import requests
from datetime import datetime

from fetchers import hackernews, rss_feeds
from processor.deduplicator import deduplicate_and_merge
from processor.summarizer import summarize, keyword_hit
import config
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
CATEGORY_ORDER = list(CATEGORIES.keys())
MIN_PER_CATEGORY_WARN = 3

# ===================================================================
# 🚀 [기능 1] URL 히스토리 및 최근 제목(재탕 방지) 관리
# ===================================================================
def load_seen() -> set:
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen: set) -> None:
    trimmed = list(seen)[-5000:]
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(trimmed))

def load_recent_titles() -> list:
    file_path = getattr(config, "RECENT_TITLES_FILE", "recent_briefing_titles.txt")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_recent_titles(new_titles: list) -> None:
    file_path = getattr(config, "RECENT_TITLES_FILE", "recent_briefing_titles.txt")
    existing = load_recent_titles()
    combined = new_titles + existing
    deduped = []
    for t in combined:
        if t not in deduped:
            deduped.append(t)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(deduped[:300]))  # 최근 300개 유지

# ===================================================================
# 🚀 [기능 2] 구글 뉴스 URL 원본 디코더
# ===================================================================
def resolve_google_news_url(url: str) -> str:
    if not url or "news.google.com" not in url:
        return url
    try:
        parsed = urllib.parse.urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        if 'articles' in path_parts:
            idx = path_parts.index('articles')
            if idx + 1 < len(path_parts):
                code = path_parts[idx + 1]
                padded = code + '=' * (-len(code) % 4)
                decoded_bytes = base64.b64decode(padded, altchars=b'-_')
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                found_urls = re.findall(r'https?://[^\s<>"{}|\^~\[\]`]+', decoded_str)
                if found_urls:
                    return found_urls[0].split('?')[0] # 파라미터 깎기
    except Exception:
        pass
    return url

# ===================================================================
# 🚀 [기능 3] Jaccard 기반 중복(재탕) 판별기
# ===================================================================
def extract_story_tokens(text: str) -> set:
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    return {word for word in text.split() if len(word) >= 2}

def is_duplicate_story(title_a: str, title_b: str, threshold: float) -> bool:
    tokens_a = extract_story_tokens(title_a)
    tokens_b = extract_story_tokens(title_b)
    if not tokens_a or not tokens_b:
        return False
    return (len(tokens_a & tokens_b) / len(tokens_a | tokens_b)) >= threshold

# ===================================================================
# 기존 헬퍼 함수들
# ===================================================================
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

# ===================================================================
# 🚀 [기능 4] 점수 엔진 고도화 (기존 relevance + 노이즈 필터링 + 재탕 패널티)
# ===================================================================
def _selection_score(article: dict, category: str, recent_titles: list) -> float:
    # 1. 기존 processor에서 매긴 AI/키워드 relevance 가져오기
    score = float(article.get("relevance", 0))
    title = article.get("title", "")
    
    # 2. 기존 로직: 해외 선호 도메인 가점
    if category in OVERSEAS_PREFERRED_DOMAINS and _article_region(article) == "global":
        score *= REGION_WEIGHT.get("global", 1.0)
        
    # 3. 신규 로직: 액션/팩트 가점
    for kw in getattr(config, "ISSUE_HIGH_VALUE_SIGNALS", []):
        if kw.lower() in title.lower(): 
            score += 3.0
            
    if re.search(r'\d+(\.\d+)?\s*(%|조|억|달러|백만|천만|만|원)', title):
        score += 4.0
        
    # 4. 신규 로직: 저가치 노이즈 폭탄 감점 (전망, 오피니언 등)
    for kw in getattr(config, "ISSUE_LOW_VALUE_SIGNALS", []):
        if kw in title: 
            score -= 14.0
            
    # 5. 신규 로직: 어제 보낸 뉴스 재탕 시 폭탄 감점
    past_threshold = getattr(config, "PAST_ISSUE_THRESHOLD", 0.65)
    penalty = getattr(config, "RECENT_ISSUE_PENALTY", -18.0)
    for past_title in recent_titles:
        if is_duplicate_story(title, past_title, past_threshold):
            score += penalty
            break
            
    return score


def send_aggregated_slack_news(articles, recent_titles) -> tuple[bool, list]:
    """카테고리별로 점수 상위 기사를 뽑아 전송하고, 전송된 기사 제목들을 반환"""
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL 이 설정되지 않았습니다.")
        return False, []

    today_str = datetime.now().strftime("%Y-%m-%d")
    buckets = {cat: [] for cat in CATEGORY_ORDER}
    for a in articles:
        cat = a.get("category", CATEGORY_ORDER[-1])
        if cat not in buckets:
            cat = CATEGORY_ORDER[-1]
        buckets[cat].append(a)

    message_text = "🗞️ *오늘의 주요 뉴스 브리핑*\n\n"
    has_news = False
    sent_titles = []

    for cat_name in CATEGORY_ORDER:
        # 고도화된 스코어링 반영
        ranked = sorted(buckets[cat_name],
                        key=lambda a: _selection_score(a, cat_name, recent_titles),
                        reverse=True)

        selected = []
        nvidia_count = 0
        for a in ranked:
            # 점수가 너무 낮아진(감점을 맞은) 기사는 과감히 스킵
            if _selection_score(a, cat_name, recent_titles) < 0:
                continue
                
            title_lower = a.get("title", "").lower()
            if "nvidia" in title_lower or "엔비디아" in title_lower:
                if nvidia_count >= 2:
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
                sent_titles.append(title)  # 히스토리 추가
            message_text += "\n"

    if not has_news:
        message_text += "오늘 조건에 맞는 새로운 뉴스가 없습니다."

    response = requests.post(slack_webhook_url, json={"text": message_text})
    if response.status_code == 200:
        print("슬랙 메시지 통합 전송 성공!")
        return True, sent_titles
    print(f"슬랙 전송 실패: {response.status_code}, {response.text}")
    return False, []


def main():
    seen = load_seen()
    recent_titles = load_recent_titles()
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
        # 🚀 [적용] 구글 뉴스 원본 링크 추출을 가장 먼저 수행
        raw_link = get_primary_link(article)
        real_link = resolve_google_news_url(raw_link)
        if isinstance(article.get("link"), list):
            article["link"][0] = real_link
        else:
            article["link"] = real_link
            
        link = real_link

        if not link or not article.get("title"):
            continue
        if link in seen:
            continue
        if not is_relevant(article):
            continue
        filtered.append(article)

    # --- 유사 기사 병합 (당일 수집분) ---
    merged, dedup_errors = deduplicate_and_merge(filtered)
    all_errors.extend(dedup_errors)

    # --- 분류 + relevance 점수 부여 (기존 AI 프로세서) ---
    classified = []
    for article in merged:
        article, sum_errors = summarize(article)
        all_errors.extend(sum_errors)
        classified.append(article)

    # 전역 컷은 피하되, 전체 내림차순 정렬
    classified.sort(key=lambda a: a.get("relevance", 0), reverse=True)

    if classified:
        # 🚀 [적용] 슬랙 발송 시 최근 제목 히스토리 전달하여 재탕 방지
        success, sent_titles = send_aggregated_slack_news(classified, recent_titles)
        if success:
            for article in classified:
                links = article.get("link", [])
                if isinstance(links, list):
                    seen.update(links)
                else:
                    seen.add(links)
            
            # 발송 성공한 기사들의 제목을 재탕 방지 리스트에 업데이트
            if sent_titles:
                save_recent_titles(sent_titles)
    else:
        print("전송할 새로운 기사가 없습니다.")

    save_seen(seen)

    # --- 수집 오류 리포트 ---
    if all_errors:
        print(f"\n⚠️ 수집 오류 {len(all_errors)}건:")
        for e in all_errors:
            print(f"  • {e}")

if __name__ == "__main__":
    main()