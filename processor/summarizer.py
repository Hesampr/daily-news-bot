import re
from config import CATEGORIES, SOFT_PENALTY_KEYWORDS, WATCHLIST_WEIGHT

try:
    from config import ALL_WATCHLISTS
except ImportError:
    ALL_WATCHLISTS = []

# 기본(미분류) 카테고리 = 거시 계열(이름이 바뀌어도 안전하게 탐색)
DEFAULT_CATEGORY = next((c for c in CATEGORIES if "거시" in c), list(CATEGORIES.keys())[-1])

_ASCII_KW = re.compile(r"[a-z0-9&\s\-\.]+")


def keyword_hit(kw: str, text_lower: str) -> bool:
    """영문·숫자 토큰은 경계 매칭(부분단어 오탐 방지), 한글 등은 부분문자열 매칭.
    - 'ai'가 'again'에 걸리지 않도록 앞뒤 영숫자 경계 확인.
    - '금리'가 '기준금리'에서 잡히도록 한글은 부분문자열(한글에 \b는 복합어 누락)."""
    kw = (kw or "").lower().strip()
    if not kw:
        return False
    if _ASCII_KW.fullmatch(kw):
        return re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", text_lower) is not None
    return kw in text_lower


def summarize(article: dict) -> tuple:
    """CATEGORIES 점수제로 분류하고, 워치리스트 가점 − 소프트감점을 relevance로 부여."""
    errors = []
    title = article.get("title", "")
    description = article.get("description") or article.get("content") or ""
    text = (title + " " + description).lower()

    scores = {cat: 0 for cat in CATEGORIES}
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if keyword_hit(kw, text):
                scores[cat] += 1

    best = max(scores, key=scores.get)
    assigned = best if scores[best] > 0 else DEFAULT_CATEGORY

    wl_hits = sum(1 for kw in ALL_WATCHLISTS if keyword_hit(kw, text))
    sp_hits = sum(1 for kw in SOFT_PENALTY_KEYWORDS if keyword_hit(kw, text))
    relevance = scores[best] + wl_hits * WATCHLIST_WEIGHT - sp_hits

    article["category"] = assigned
    article["category_scores"] = scores
    article["relevance"] = max(float(relevance), 0.0)
    return article, errors
