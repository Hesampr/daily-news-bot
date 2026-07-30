import os
import re
import requests
from datetime import datetime

from fetchers import hackernews, rss_feeds
try:
    from fetchers import newsletters
    HAS_NEWSLETTERS = True
except ImportError:
    HAS_NEWSLETTERS = False
    print("ℹ️ 뉴스레터 모듈을 찾을 수 없어 수집 단계에서 제외합니다.")

from processor.deduplicator import deduplicate_and_merge
from processor.summarizer import summarize, keyword_hit
from processor.reranker import rerank_by_category, is_enabled as llm_enabled
from config import (
    INTEREST_KEYWORDS,
    BLACKLIST_KEYWORDS,
    HN_KEYWORDS,
    CATEGORIES,
    MAX_PER_CATEGORY_DICT,
    MAX_PER_CATEGORY,
    OVERSEAS_PREFERRED_DOMAINS,
    REGION_WEIGHT,
)
try:
    from config import LLM_SEND_MIN_SCORE
except ImportError:
    LLM_SEND_MIN_SCORE = 0

SEEN_FILE = "seen_news.txt"
SEEN_TITLES_FILE = "seen_titles.txt"
CATEGORY_ORDER = list(CATEGORIES.keys())
MIN_PER_CATEGORY_WARN = 3


def _load_lines(path) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def _save_lines(path, items, cap=5000):
    with open(path, "w", encoding="utf-8") as f:
        # sorted()를 추가하여 항상 일정한 순서로 저장되게 만듭니다.
        f.write("\n".join(sorted(list(items))[-cap:]))
        

def is_same_news_issue(title_a: str, title_b: str, threshold: float = 0.65) -> bool:
    tokens_a = {w for w in re.sub(r'[^\w\s]', ' ', title_a.lower()).split() if len(w) >= 2}
    tokens_b = {w for w in re.sub(r'[^\w\s]', ' ', title_b.lower()).split() if len(w) >= 2}
    if not tokens_a or not tokens_b:
        return False
    return (len(tokens_a & tokens_b) / len(tokens_a | tokens_b)) >= threshold


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


def get_primary_source(article: dict) -> str:
    src = article.get("source", "")
    if isinstance(src, list):
        return src[0] if src else ""
    return src


def clean_source_name(source: str) -> str:
    mapping = {
        "ImpactOn (임팩트온)": "임팩트온",
        "ImpactOn": "임팩트온",
        "Platum (플랫텀)": "플랫텀",
        "VentureSquare (벤처스퀘어)": "벤처스퀘어",
        "VentureSquare": "벤처스퀘어",
        "한경 Geeks (벤처/VC)": "한경 Geeks",
        "전자신문 (벤처/스타트업)": "전자신문",
        "Trellis (구 GreenBiz)": "Trellis",
        "The Batch (deeplearning.ai)": "The Batch",
        "SemiAnalysis (칩/인프라)": "SemiAnalysis",
        "Sifted (EU 스타트업)": "Sifted",
    }
    if source in mapping:
        return mapping[source]
    cleaned = re.sub(r'\s*\(.*?\)', '', source).strip()
    return cleaned if cleaned else source


def fmt_date(date_str: str) -> str:
    for fmt in ("%Y-%m-%d",):
        try:
            return datetime.strptime(date_str, fmt).strftime("%y.%m.%d")
        except (ValueError, TypeError):
            pass
    return datetime.now().strftime("%y.%m.%d")


def _article_region(article: dict) -> str:
    return article.get("region", "global")


def _selection_score(article: dict, category: str) -> float:
    llm = article.get("llm_score")
    if llm is not None:
        return float(llm)
    score = float(article.get("relevance", 0))
    if category in OVERSEAS_PREFERRED_DOMAINS and _article_region(article) == "global":
        score *= REGION_WEIGHT.get("global", 1.0)
    return score


def send_aggregated_slack_news(articles) -> bool:
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL 이 설정되지 않았습니다.")
        return False

    buckets = {cat: [] for cat in CATEGORY_ORDER}
    for a in articles:
        cat = a.get("category", CATEGORY_ORDER[-1])
        if cat not in buckets:
            cat = CATEGORY_ORDER[-1]
        buckets[cat].append(a)

    message_text = "🗞️ *오늘의 주요 뉴스 브리핑*\n\n"
    has_news = False

    for cat_name in CATEGORY_ORDER:
        max_limit = MAX_PER_CATEGORY_DICT.get(cat_name, MAX_PER_CATEGORY)
        ranked = sorted(buckets[cat_name], key=lambda a: _selection_score(a, cat_name), reverse=True)
        selected, nvidia = [], 0
        
        for a in ranked:
            tl = a.get("title", "").lower()
            if "nvidia" in tl or "엔비디아" in tl:
                if nvidia >= 2:
                    continue
                nvidia += 1
            if a.get("llm_score") is not None and a["llm_score"] < LLM_SEND_MIN_SCORE:
                continue
            selected.append(a)
            if len(selected) >= max_limit:
                break

        if len(selected) < MIN_PER_CATEGORY_WARN and cat_name != "👔 MBB·Big4 인사이트":
            for a in ranked:
                if a in selected:
                    continue
                tl = a.get("title", "").lower()
                if ("nvidia" in tl or "엔비디아" in tl) and nvidia >= 2:
                    continue
                selected.append(a)
                if len(selected) >= MIN_PER_CATEGORY_WARN:
                    break

        if selected:
            has_news = True
            message_text += f"*{cat_name}*\n"
            for a in selected:
                title = a.get("title", "제목 없음").strip()
                url = get_primary_link(a) or "#"
                raw_source = get_primary_source(a) or "출처미상"
                source = clean_source_name(raw_source)
                date = fmt_date(a.get("date", ""))
                message_text += f"• <{url}|{title}> ({source}, {date})\n"
            message_text += "\n"

    if not has_news:
        message_text += "오늘 조건에 맞는 새로운 뉴스가 없습니다."

    resp = requests.post(slack_webhook_url, json={"text": message_text})
    if resp.status_code == 200:
        print("슬랙 메시지 통합 전송 성공!")
        return True
    print(f"슬랙 전송 실패: {resp.status_code}, {resp.text}")
    return False


def main():
    seen_links = set(_load_lines(SEEN_FILE))
    seen_titles = _load_lines(SEEN_TITLES_FILE)
    all_errors, all_articles = [], []

    hn_articles, hn_errors = hackernews.fetch(HN_KEYWORDS)
    all_errors.extend(hn_errors)
    all_articles.extend(hn_articles)
    
    if HAS_NEWSLETTERS:
        try:
            print("📬 뉴스레터 수집 시도 중...")
            nl_articles, nl_errors = newsletters.fetch()
            all_errors.extend(nl_errors)
            all_articles.extend(nl_articles)
            print(f"📬 뉴스레터 {len(nl_articles)}건 수집 완료")
        except Exception as e:
            print(f"⚠️ 뉴스레터 수집 중 에러 발생 (스킵합니다): {e}")
            all_errors.append(f"뉴스레터 수집 실패: {str(e)}")
    else:
        print("⏩ 뉴스레터 수집 기능이 비활성화되어 넘어갑니다.")
        
    rss_articles, rss_errors = rss_feeds.fetch()
    all_errors.extend(rss_errors)
    all_articles.extend(rss_articles)

    filtered = []
    for art in all_articles:
        link = get_primary_link(art)
        title = art.get("title", "")
        if not link or not title:
            continue
        if link in seen_links:
            continue
        if any(is_same_news_issue(title, old) for old in seen_titles[-800:]):
            continue
        if not is_relevant(art):
            continue
        filtered.append(art)

    merged, dedup_errors = deduplicate_and_merge(filtered)
    all_errors.extend(dedup_errors)

    classified = []
    for art in merged:
        art, e = summarize(art)
        all_errors.extend(e)
        classified.append(art)
    classified.sort(key=lambda a: a.get("relevance", 0), reverse=True)

    classified = rerank_by_category(classified, CATEGORY_ORDER)
    if llm_enabled():
        print("LLM 리랭크 적용됨 (Gemini)")

    if classified:
        if send_aggregated_slack_news(classified):
            for art in classified:
                links = art.get("link", [])
                seen_links.update(links if isinstance(links, list) else [links])
                seen_titles.append(art.get("title", ""))
    else:
        print("전송할 새로운 기사가 없습니다.")

    _save_lines(SEEN_FILE, seen_links)
    _save_lines(SEEN_TITLES_FILE, seen_titles, cap=2000)

    if all_errors:
        print(f"\n⚠️ 수집 오류 {len(all_errors)}건:")
        for e in all_errors:
            print(f"  • {e}")


if __name__ == "__main__":
    main()
