import re
from config import (
    CATEGORIES,
    SOFT_PENALTY_KEYWORDS,
    WATCHLIST_WEIGHT,
    ALL_WATCHLISTS,
    SOURCE_CATEGORY_OVERRIDE  # 🚀 Override 딕셔너리 임포트
)

def keyword_hit(keyword: str, text: str) -> bool:
    kw_lower = keyword.lower()
    if re.search(r'[a-z]', kw_lower):
        # 영문은 단어 경계 매칭
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        return bool(re.search(pattern, text))
    else:
        # 국문은 포함 여부
        return kw_lower in text

def summarize(article: dict):
    errors = []
    title = article.get("title", "")
    desc = article.get("description", "") or article.get("summary", "")
    text = (title + " " + desc).lower()
    
    source = article.get("source", "")
    if isinstance(source, list):
        source = source[0] if source else ""
    source_clean = source.strip()

    assigned_category = None
    base_score = 0.0

    # 🚀 [1단계] 출처 Override (가장 강함)
    if source_clean in SOURCE_CATEGORY_OVERRIDE:
        assigned_category = SOURCE_CATEGORY_OVERRIDE[source_clean]
        base_score += 3.0  # 신뢰할 수 있는 전문 매체는 묻지도 따지지도 않고 강력한 가점 부여

    # 🚀 [2단계] 명확한 키워드 검사
    category_scores = {cat: 0 for cat in CATEGORIES}
    for cat, kws in CATEGORIES.items():
        hits = sum(1 for kw in kws if keyword_hit(kw, text))
        category_scores[cat] = hits

    # 종합 매체(Reuters, Google News 등)처럼 출처 고정이 안 된 곳만 키워드로 카테고리 결정
    if not assigned_category:
        if sum(category_scores.values()) > 0:
            assigned_category = max(category_scores, key=category_scores.get)
        else:
            # 매칭 없으면 기본 fallback
            assigned_category = list(CATEGORIES.keys())[-1]
    
    # 키워드 점수 합산 (전문 매체 기사라도 우리 타겟 키워드가 많으면 우선순위 떡상)
    if assigned_category in category_scores:
        base_score += float(category_scores[assigned_category])

    # 🚀 [3단계] 관심 기업(Watchlist) 및 페널티 적용
    for w_kw in ALL_WATCHLISTS:
        if keyword_hit(w_kw, text):
            base_score += float(WATCHLIST_WEIGHT)
            
    for p_kw in SOFT_PENALTY_KEYWORDS:
        if keyword_hit(p_kw, text):
            base_score -= 1.0

    # 최종 적용
    article["category"] = assigned_category
    article["relevance"] = max(0.0, base_score) # 점수가 마이너스로 떨어지지 않게 방어
    
    return article, errors
