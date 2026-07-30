import os
import re
import json
import requests
from config import MAX_PER_CATEGORY_DICT, MAX_PER_CATEGORY

# LLM 장애 시 폴백 품질용: 투자자 관점의 '사건 발생' 시그널
INVESTMENT_SIGNAL_KEYWORDS = [
    "raise", "raised", "raises", "funding", "fund", "investment", "invest",
    "acquisition", "acquire", "merger", "series", "seed", "ipo", "valuation",
    "regulation", "policy", "launch", "deal", "stake", "buyout",
    "투자유치", "투자", "인수", "합병", "펀딩", "상장", "출자", "규제", "정책",
]

def is_enabled():
    return bool(os.environ.get("GEMINI_API_KEY"))

def select_top_news_with_llm(articles: list, category_order: list) -> list:
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    if not model_name or model_name.strip() == "":
        model_name = "gemini-flash-latest"

    buckets = {cat: [] for cat in category_order}
    for a in articles:
        cat = a.get("category", category_order[-1])
        if cat not in buckets:
            cat = category_order[-1]
        buckets[cat].append(a)

    candidates = {}
    id_counter = 1
    prompt_text = "다음은 오늘 수집된 뉴스 기사 후보들이다. 심사역/VC 파트너 입장에서 꼭 읽어야 할 핵심 기사만 고르려고 한다.\n\n[후보 리스트]\n"

    for cat in category_order:
        # 🚀 피드백 반영: 구글 뉴스 비율 증가에 맞춰 카테고리당 후보군을 10개로 확대
        ranked = sorted(buckets[cat], key=lambda x: float(x.get("relevance", 0)), reverse=True)[:10]
        for a in ranked:
            a["_temp_id"] = str(id_counter)
            candidates[str(id_counter)] = a

            title = a.get("title", "")
            source = a.get("source", "")
            desc = (a.get("summary", "") or a.get("description", ""))[:180]

            prompt_text += f"ID [{id_counter}] | 분야: {cat} | 언론사: {source}\n제목: {title}\n요약: {desc}\n---\n"
            id_counter += 1

    if not candidates:
        return []

    if not api_key:
        print("ℹ️ GEMINI_API_KEY가 없어 다단계 규칙 기반 Fallback 순으로 선정합니다.")
        return _fallback_rule_based(buckets, category_order)

    limit_instructions = ", ".join([f"'{c}' 최대 {MAX_PER_CATEGORY_DICT.get(c, MAX_PER_CATEGORY)}개" for c in category_order])

    # 🚀 피드백 반영: VC 투자자 관점의 구체적인 선택/제외 기준 프롬프트 추가
    instruction = (
        prompt_text +
        f"\n[지시사항]\n"
        f"1. 각 분야별로 가장 중요한 기사만 선택해라. ({limit_instructions})\n"
        f"2. 투자자에게 새로운 정보가 있는 기사, 실제 투자·시장·정책 변화가 발생한 기사를 최우선으로 고른다.\n"
        f"3. 단순 의견, 인터뷰, 행사·세미나 홍보, 지자체 지원사업, 주가 전망 리딩 기사는 철저히 제외한다.\n"
        f"3-1. 동일 기업(예: Nvidia, OpenAI)에 관한 기사는 한 분야당 최대 2개까지만 선택한다.\n"
        f"4. 설명이나 요약은 절대 쓰지 말고, 오직 선택한 기사의 ID 숫자들만 JSON 형식으로 반환해라.\n"
        f'응답 예시: {{"selected": ["1", "3", "8", "12"]}}'
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": instruction}]}],
        # 🚀 피드백 반영: 매일 일관된 핵심 선택을 위해 temperature 0.0 고정
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.0}
    }

    try:
        print(f"🧠 제미나이 편집장({model_name})이 핵심 뉴스를 선별 중입니다... (Top 10 후보군, 1회 호출)")
        # 🚀 피드백 반영: 깃허브 액션 환경의 타임아웃 방지를 위해 30초로 상향
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        raw_json = data["candidates"][0]["content"]["parts"][0]["text"]

        # ✅ 6번 버그 수정: Gemini가 숫자(1)/문자("1")/"ID 3"/"#3" 등 뭘 줘도 숫자만 뽑아 매칭
        raw_selected = json.loads(raw_json).get("selected", [])
        selected_ids = []
        for x in raw_selected:
            digits = re.sub(r"\D", "", str(x))   # "ID 3" -> "3", 3 -> "3"
            if digits:
                selected_ids.append(digits)

        # 범위밖/중복 id 제거하면서 순서 보존
        final_articles = []
        seen = set()
        for sid in selected_ids:
            if sid in candidates and sid not in seen:
                seen.add(sid)
                final_articles.append(candidates[sid])

        # ✅ 6번: 선택 결과가 비면(파싱 이상/전부 범위밖) 규칙 폴백으로
        if not final_articles:
            print("⚠️ 제미나이 선택 결과가 비어 있어 규칙 기반 Fallback으로 전환합니다.")
            return _fallback_rule_based(buckets, category_order)

        print(f"✨ 제미나이 선별 완료: 후보 {len(candidates)}개 중 {len(final_articles)}개 선택됨!")
        return final_articles

    except Exception as e:
        print(f"⚠️ 제미나이 API 호출 실패 ({e}) -> 3단계 안전 Fallback 모드로 전환합니다!")
        return _fallback_rule_based(buckets, category_order)


def _fallback_rule_based(buckets: dict, category_order: list) -> list:
    """
    🚀 피드백 반영: LLM 실패 시 3단계 정렬 (1. Global 우선 -> 2. Relevance 높은 순 -> 3. Watchlist 여부)
    """
    fallback_list = []
    for cat in category_order:
        max_limit = MAX_PER_CATEGORY_DICT.get(cat, MAX_PER_CATEGORY)

        def fallback_sort_key(art):
            text = (art.get("title", "") + " " + art.get("description", "")).lower()
            # ✅ #2 반영: '단순 점수'가 아니라 투자자 관점 '사건 시그널'을 최우선
            signal_score = sum(1 for kw in INVESTMENT_SIGNAL_KEYWORDS if kw in text)
            is_global = 1 if art.get("region", "global") == "global" else 0
            relevance_score = float(art.get("relevance", 0))
            return (signal_score, is_global, relevance_score)

        ranked = sorted(buckets[cat], key=fallback_sort_key, reverse=True)
        fallback_list.extend(ranked[:max_limit])
    return fallback_list

def rerank_by_category(articles: list, category_order: list) -> list:
    return select_top_news_with_llm(articles, category_order)
