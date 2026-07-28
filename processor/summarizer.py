import re
from config import CATEGORIES

def summarize(article: dict) -> tuple:
    """
    Gemini AI 대신 config.py의 CATEGORIES 키워드 매칭(점수제)으로 
    기사를 4대 카테고리로 자동 분류합니다.
    """
    errors = []
    title = article.get("title", "")
    description = article.get("description") or article.get("content") or ""
    text = (title + " " + description).lower()

    # 카테고리별 키워드 일치 개수 계산
    category_scores = {
        "🌱 임팩트": 0,
        "🤖 AI": 0,
        "💼 대체투자": 0,
        "🌐 거시경제": 0
    }

    for cat_name, keywords in CATEGORIES.items():
        if not cat_name or cat_name not in category_scores:
            continue
            
        for kw in keywords:
            if not kw:
                continue
            # 단어 경계(\b)를 사용해 정확히 일치하는 키워드 개수 카운트
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, text):
                category_scores[cat_name] += 1

    # 가장 매칭 점수가 높은 카테고리 선정
    best_category = max(category_scores, key=category_scores.get)
    
    # 일치하는 키워드가 단 하나도 없는 경우 기본값으로 '🌐 거시경제' 지정
    if category_scores[best_category] == 0:
        assigned_category = "🌐 거시경제"
    else:
        assigned_category = best_category

    # 결과 저장
    article["category"] = assigned_category
    return article, errors
