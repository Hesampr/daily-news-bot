import os
import json
import requests

def is_enabled():
    return bool(os.environ.get("GEMINI_API_KEY"))

def select_top_news_with_llm(articles: list, category_order: list, max_per_cat: int = 4) -> list:
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    if not model_name or model_name.strip() == "":
        model_name = "gemini-1.5-flash"

    buckets = {cat: [] for cat in category_order}
    for a in articles:
        cat = a.get("category", category_order[-1])
        if cat not in buckets:
            cat = category_order[-1]
        buckets[cat].append(a)

    candidates = {}
    id_counter = 1
    prompt_text = "다음은 오늘 수집된 뉴스 기사 후보들이다. 심사역/투자자 입장에서 꼭 읽어야 할 핵심 기사만 고르려고 한다.\n\n[후보 리스트]\n"

    for cat in category_order:
        ranked = sorted(buckets[cat], key=lambda x: float(x.get("relevance", 0)), reverse=True)[:7]
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
        print("ℹ️ GEMINI_API_KEY가 없어 규칙 기반 점수 순으로 선정합니다.")
        return _fallback_rule_based(buckets, category_order, max_per_cat)

    instruction = (
        prompt_text + 
        f"\n[지시사항]\n"
        f"1. 각 분야({', '.join(category_order)})별로 가장 중요한 기사를 최대 {max_per_cat}개씩만 선택해라.\n"
        f"2. 지방자치단체 지원사업, 소상공인 대출, 단순 지역 행사, 연예/가십성 노이즈는 무조건 탈락시켜라.\n"
        f"3. 설명이나 요약은 절대 쓰지 말고, 오직 선택한 기사의 ID 숫자들만 JSON 형식으로 반환해라.\n"
        f'응답 예시: {{"selected": ["1", "3", "8", "12"]}}'
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": instruction}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}
    }

    try:
        print(f"🧠 제미나이 편집장({model_name})이 핵심 뉴스를 선별 중입니다... (1회 호출)")
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        
        data = resp.json()
        raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
        selected_ids = json.loads(raw_json).get("selected", [])
        
        final_articles = [candidates[sid] for sid in selected_ids if sid in candidates]
        print(f"✨ 제미나이 선별 완료: 후보 {len(candidates)}개 중 {len(final_articles)}개 선택됨!")
        return final_articles

    except Exception as e:
        print(f"⚠️ 제미나이 API 호출 실패 ({e}) -> 규칙 기반 Fallback 모드로 전환합니다!")
        return _fallback_rule_based(buckets, category_order, max_per_cat)


def _fallback_rule_based(buckets: dict, category_order: list, max_per_cat: int) -> list:
    fallback_list = []
    for cat in category_order:
        ranked = sorted(buckets[cat], key=lambda x: float(x.get("relevance", 0)), reverse=True)
        fallback_list.extend(ranked[:max_per_cat])
    return fallback_list

def rerank_by_category(articles: list, category_order: list) -> list:
    return select_top_news_with_llm(articles, category_order, max_per_cat=4)
