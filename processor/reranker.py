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

_API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
_DEAD_PREFIXES = ("gemini-1.0", "gemini-1.5", "gemini-2.0")
# 이 키/프로젝트에서 살아있는 모델을 못 찾으면 순서대로 시도할 후보들
_MODEL_CANDIDATES = [
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-flash-lite-latest",
]
_RESOLVED_MODEL = None   # 한 번 성공한 모델은 프로세스 내 캐시


def is_enabled():
    return bool(os.environ.get("GEMINI_API_KEY"))


def _candidate_models():
    env = os.environ.get("GEMINI_MODEL", "").strip()
    chain = []
    if env and not env.startswith(_DEAD_PREFIXES):
        chain.append(env)
    for m in _MODEL_CANDIDATES:
        if m not in chain:
            chain.append(m)
    return chain


def _post_generate(model: str, api_key: str, instruction: str, timeout: int = 30) -> str:
    url = f"{_API_ROOT}/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": instruction}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.0},
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _discover_model(api_key: str, timeout: int = 15):
    """ListModels 로 실제 사용 가능한 flash 계열 generateContent 모델을 찾는다."""
    url = f"{_API_ROOT}/models?key={api_key}&pageSize=100"
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    models = resp.json().get("models", [])
    flashes = []
    for m in models:
        name = m.get("name", "").split("/")[-1]
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods and "flash" in name and not name.startswith(_DEAD_PREFIXES):
            flashes.append(name)
    # lite(저비용) 우선, 그다음 이름 순
    flashes.sort(key=lambda n: (0 if "lite" in n else 1, n))
    return flashes[0] if flashes else None


def _call_llm(instruction: str, api_key: str):
    """후보 체인 → 실패 시 ListModels 자동탐색. 성공 시 (text, used_model), 실패 시 (None, None)."""
    global _RESOLVED_MODEL
    tried = []
    order = ([_RESOLVED_MODEL] if _RESOLVED_MODEL else []) + _candidate_models()
    for model in order:
        if not model or model in tried:
            continue
        tried.append(model)
        try:
            text = _post_generate(model, api_key, instruction)
            _RESOLVED_MODEL = model
            return text, model
        except requests.HTTPError as e:
            code = getattr(e.response, "status_code", None)
            if code == 404:
                continue          # 이 모델 없음 → 다음 후보
            print(f"⚠️ Gemini HTTP {code} ({model}) — 다음 후보로.")
            continue
        except Exception as e:
            print(f"⚠️ Gemini 호출 예외 ({model}): {e} — 다음 후보로.")
            continue

    # 후보 전부 실패 → ListModels 자동탐색
    try:
        disc = _discover_model(api_key)
        if disc and disc not in tried:
            print(f"🔎 ListModels 로 사용 가능한 모델 탐색 → {disc}")
            text = _post_generate(disc, api_key, instruction)
            _RESOLVED_MODEL = disc
            return text, disc
    except Exception as e:
        print(f"⚠️ ListModels 탐색 실패: {e}")
    return None, None


def select_top_news_with_llm(articles: list, category_order: list) -> list:
    api_key = os.environ.get("GEMINI_API_KEY")

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

    print("🧠 제미나이 편집장이 핵심 뉴스를 선별 중입니다... (Top 10 후보군)")
    raw_json, used_model = _call_llm(instruction, api_key)
    if raw_json is None:
        print("⚠️ 사용 가능한 Gemini 모델을 찾지 못해 규칙 기반 Fallback으로 전환합니다.")
        return _fallback_rule_based(buckets, category_order)

    try:
        raw_selected = json.loads(raw_json).get("selected", [])
        # 숫자(1)/문자("1")/"ID 3"/"#1" 뭐가 와도 숫자만 추출
        selected_ids = []
        for x in raw_selected:
            digits = re.sub(r"\D", "", str(x))
            if digits:
                selected_ids.append(digits)

        final_articles, seen = [], set()
        for sid in selected_ids:
            if sid in candidates and sid not in seen:
                seen.add(sid)
                final_articles.append(candidates[sid])

        if not final_articles:
            print("⚠️ 제미나이 선택 결과가 비어 있어 규칙 기반 Fallback으로 전환합니다.")
            return _fallback_rule_based(buckets, category_order)

        print(f"✨ 제미나이({used_model}) 선별 완료: 후보 {len(candidates)}개 중 {len(final_articles)}개 선택!")
        return final_articles

    except Exception as e:
        print(f"⚠️ 제미나이 응답 파싱 실패 ({e}) -> 규칙 기반 Fallback으로 전환합니다.")
        return _fallback_rule_based(buckets, category_order)


def _fallback_rule_based(buckets: dict, category_order: list) -> list:
    """LLM 실패 시: 투자자 시그널 -> Global -> relevance 순."""
    fallback_list = []
    for cat in category_order:
        max_limit = MAX_PER_CATEGORY_DICT.get(cat, MAX_PER_CATEGORY)

        def fallback_sort_key(art):
            text = (art.get("title", "") + " " + art.get("description", "")).lower()
            signal_score = sum(1 for kw in INVESTMENT_SIGNAL_KEYWORDS if kw in text)
            is_global = 1 if art.get("region", "global") == "global" else 0
            relevance_score = float(art.get("relevance", 0))
            return (signal_score, is_global, relevance_score)

        ranked = sorted(buckets[cat], key=fallback_sort_key, reverse=True)
        fallback_list.extend(ranked[:max_limit])
    return fallback_list


def rerank_by_category(articles: list, category_order: list) -> list:
    return select_top_news_with_llm(articles, category_order)
