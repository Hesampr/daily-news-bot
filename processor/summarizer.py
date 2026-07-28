import os
import time
from google import genai

_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

def summarize(article: dict) -> tuple:
    """
    기존 요약 대신 기사 제목과 본문을 읽고 4대 카테고리 중 하나로 분류합니다.
    (bot.py와의 연결을 위해 함수명 summarize 유지)
    """
    errors = []
    title = article.get("title", "").strip()
    description = article.get("description") or article.get("content") or ""
    
    prompt = f"""
다음 뉴스 기사의 제목과 본문을 읽고, 아래 [카테고리 지침]에 따라 가장 적합한 카테고리 '이름만' 출력하세요. 다른 설명이나 요약문은 절대 포함하지 마세요.

[카테고리 지침]
1. 🌱 임팩트: 소셜임팩트, ESG, 기후테크, 돌봄, 시니어, 에너지, 순환경제, 임팩트 투자, 친환경 규제 및 정책 관련 뉴스
2. 🤖 AI: 생성형 AI, LLM, 머신러닝, 인공지능 기술 및 산업 관련 뉴스
3. 💼 대체투자 (PE, VC, AC): 사모펀드, 벤처캐피탈, 액셀러레이터, 스타트업 투자, M&A 관련 뉴스
4. 🌐 거시경제: 금리, 환율, 인플레이션, 미 연준(Fed), 국내외 경제 동향 관련 뉴스

기사 제목: {title}
기사 본문: {description[:500]}

반드시 다음 4개 중 하나로만 정확히 출력하세요: [🌱 임팩트, 🤖 AI, 💼 대체투자 (PE, VC, AC), 🌐 거시경제]
"""
    category = "🌐 거시경제"  # 기본값 (분류 실패 시)
    try:
        response = _client.models.generate_content(
            model="gemini-1.5-flash",  # 1.5-flash 모델로 변경 완료
            contents=prompt,
        )
        time.sleep(2)  # 연속 호출 시 API 보호를 위해 2초 대기
        text = response.text.strip()
        print(f"Gemini category response: {text}", flush=True)
        
        valid_categories = ["🌱 임팩트", "🤖 AI", "💼 대체투자 (PE, VC, AC)", "🌐 거시경제"]
        for valid in valid_categories:
            if valid in text:
                category = valid
                break
    except Exception as e:
        print(f"Gemini classification error: {str(e)}", flush=True)
        errors.append(f"Classification failed for '{title}': {str(e)}")

    # 분류된 카테고리 저장
    article["category"] = category
    return article, errors
