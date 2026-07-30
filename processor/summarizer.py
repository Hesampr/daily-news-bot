import re
from config import (
    CATEGORIES,
    SOFT_PENALTY_KEYWORDS,
    WATCHLIST_WEIGHT,
    ALL_WATCHLISTS,
    RSS_SOURCE_METADATA
)

def keyword_hit(keyword: str, text: str) -> bool:
    kw_lower = keyword.lower()
    if re.search(r'[a-z]', kw_lower):
        # 영문은 단어 경계(word boundary) 매칭을 통해 엄격하게 검사 ('ai'가 'email'에 걸리지 않도록)
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        return bool(re.search(pattern, text))
    else:
        # 국문은 포함 여부로 검사
        return kw_lower in text

def summarize(article: dict):
    """
    [카테고리 할당 및 관련도 점수 산정 로직]
    1. 출처(Source) 기반 카테고리 우선 부여 (전문 매체 신뢰)
    2. 종합 매체/Google News는 키워드 매칭 빈도 기반 분류
    3. Watchlist 가중치 합산 및 노이즈 페널티 차감
    """
    errors = []
    title = article.get("title", "")
    desc = article.get("description", "") or article.get("summary", "")
    text = (title + " " + desc).lower()
    
    source = article.get("source", "")
    if isinstance(source, list):
        source = source[0] if source else ""

    assigned_category = None
    base_score = 0.0

    # 🚀 [1단계] 출처 기반 강력한 카테고리 우선 배정
    source_meta = RSS_SOURCE_METADATA.get(source)
    if source_meta:
        assigned_category = source_meta.get("category")
        base_score += 2.0  # 전문 매체에서 온 기사는 기본 신뢰도(가중치) 강력 부여

    # 🚀 [2단계] 카테고리별 키워드 매칭 점수 계산
    category_scores = {cat: 0 for cat in CATEGORIES}
    for cat, kws in CATEGORIES.items():
        hits = sum(1 for kw in kws if keyword_hit(kw, text))
        category_scores[cat] = hits

    # 출처 맵핑이 없는 종합매체(Google News, Hacker News 등) 처리
    if not assigned_category:
        if sum(category_scores.values()) > 0:
            # 키워드가 가장 많이 매칭된 카테고리로 할당
            assigned_category = max(category_scores, key=category_scores.get)
        else:
            # 매칭이 없으면 가장 마지막 카테고리(보통 인사이트/기타)로 Fallback
            assigned_category = list(CATEGORIES.keys())[-1]
    
    # 키워드 히트 점수를 최종 점수에 합산 (전문 매체 기사라도 키워드가 많으면 점수 상승)
    if assigned_category in category_scores:
        base_score += float(category_scores[assigned_category])

    # 🚀 [3단계] 관심 기업(Watchlist) 가중치 및 페널티 적용
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
