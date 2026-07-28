"""LLM 리랭커 (Gemini, 선택).
- GEMINI_API_KEY 없으면 그대로 통과(규칙 랭킹 유지) → 결정론 기본, LLM은 얹기.
- 전역 Top-N이 아니라 '카테고리별'로 재랭킹 → 5대분류 균형/굶김 방지.
- 반환 id 범위·중복 검증, JSON 파싱/타임아웃 실패 시 해당 카테고리는 규칙 랭킹으로 폴백.
- 새 의존성 없음(requests REST 호출).
"""
import os
import re
import json
import requests

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
CANDIDATES_PER_CATEGORY = 14      # 카테고리별 LLM에 보낼 후보 수(비용 상한)
DESC_LIMIT = 300


def is_enabled() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def _call_gemini(prompt: str, timeout: int = 40) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    url = _ENDPOINT.format(model=GEMINI_MODEL)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,                 # 날짜별 흔들림 최소화
            "responseMimeType": "application/json",
        },
    }
    resp = requests.post(url, params={"key": key}, json=body, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _build_prompt(category: str, items: list) -> str:
    blocks = []
    for i, a in enumerate(items, 1):
        desc = (a.get("description") or "")[:DESC_LIMIT]
        blocks.append(f"[{i}] Title: {a.get('title','')}\nSource: {a.get('source')}\nDescription: {desc}")
    joined = "\n\n".join(blocks)
    return (
        f"당신은 임팩트 지향 VC 심사역입니다. 아래는 '{category}' 카테고리의 후보 기사입니다.\n"
        "각 기사에 대해 투자 영향도, 시장 파급력, 신규성, 산업 중요도를 기준으로 0~100 점수를 매기고 "
        "중요도 높은 순으로 정렬하세요. 홍보/단순전망/수혜주/재탕 기사는 낮게 주세요.\n"
        "반드시 JSON만 반환하세요. 형식:\n"
        '{"ranking":[{"id":3,"score":92},{"id":1,"score":85}]}\n\n'
        f"기사\n{joined}\n"
    )


def _parse_ranking(text: str, n: int):
    """(1-based id, score) 리스트 반환. 범위밖/중복 제거."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    obj = json.loads(text)
    raw = obj.get("ranking")
    if raw is None:
        raw = obj.get("selected") or []
    out, seen = [], set()
    for r in raw:
        if isinstance(r, dict):
            i, s = r.get("id"), r.get("score", 0)
        else:
            i, s = r, 0
        try:
            i = int(i)
        except (TypeError, ValueError):
            continue
        if 1 <= i <= n and i not in seen:
            seen.add(i)
            try:
                s = float(s)
            except (TypeError, ValueError):
                s = 0.0
            out.append((i, s))
    return out


def rerank_by_category(classified: list, category_order: list) -> list:
    """카테고리별로 LLM 점수를 매겨 article['llm_score']에 기록. 실패/무키 시 원본 유지."""
    if not is_enabled():
        return classified

    buckets = {c: [] for c in category_order}
    for a in classified:
        c = a.get("category")
        if c in buckets:
            buckets[c].append(a)

    for cat, items in buckets.items():
        cand = sorted(items, key=lambda a: a.get("relevance", 0), reverse=True)[:CANDIDATES_PER_CATEGORY]
        if len(cand) < 2:
            continue
        try:
            text = _call_gemini(_build_prompt(cat, cand))
            ranked = _parse_ranking(text, len(cand))
            if not ranked:
                continue
            score_map = {i - 1: s for i, s in ranked}
            for idx, a in enumerate(cand):
                a["llm_score"] = score_map.get(idx, 0.0)   # 후보인데 미랭크 → 0
        except Exception:
            continue     # 이 카테고리만 규칙 랭킹 유지
    return classified
