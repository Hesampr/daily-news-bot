import re
from config import (
    CATEGORIES,
    SOFT_PENALTY_KEYWORDS,
    WATCHLIST_WEIGHT,
    ALL_WATCHLISTS,
    RSS_SOURCE_METADATA  # 🚀 메타데이터 임포트
)

def keyword_hit(keyword: str, text: str) -> bool:
    kw_lower = keyword.lower()
    if re.search(r'[a-z]', kw_lower):
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        return bool(re.search(pattern, text))
    else:
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

    # 🚀 [1단계] 출처 기반 카테고리 강제 지정 및 Priority 적용
    source_meta = RSS_SOURCE_METADATA.get(source_clean)
    if source_meta:
        assigned_category = source_meta.get("category")
        # 메타데이터에 정의된 강력한 우선순위(Priority 4~5점)를 기본 점수로 부여
        base_score += float(source_meta.get("priority", 0))

    # 🚀 [2단계] 키워드 보정 (종합 매체 분류 & 전문 매체 가점)
    category_scores = {cat: 0 for cat in CATEGORIES}
    for cat, kws in CATEGORIES.items():
        hits = sum(1 for kw in kws if keyword_hit(kw, text))
        category_scores[cat] = hits

    # 메타데이터에 없는 종합 매체(구글 뉴스, 해커뉴스 등)는 키워드로 카테고리 결정
    if not assigned_category:
        if sum(category_scores.values()) > 0:
            assigned_category = max(category_scores, key=category_scores.get)
        else:
            assigned_category = list(CATEGORIES.keys())[-1] # Fallback
    
    # 전문 매체 기사라도 우리 타겟 키워드가 많으면 추가 가점 (+보정)
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
    article["relevance"] = max(0.0, base_score) # 점수 마이너스 방지
    
    return article, errors
