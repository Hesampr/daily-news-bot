# -*- coding: utf-8 -*-
# ============================================================================
#  임팩트 VC 뉴스 클리핑 봇 - config (v3)
#  이번 확장 초점:  💼 대체투자(AC/VC/PE)  ·  🤖 AI   (임팩트/거시는 유지)
#  표기:  # ➕추가  # 📊시트도출  # ❓확인필요
#
#  ★ 구조 변경: 카테고리별 키워드를 '한 번만' 정의하고, 수집필터(INTEREST_KEYWORDS)는
#     그로부터 자동 생성 → 두 리스트가 어긋나던 문제 제거. 키워드는 아래 *_KW 에만 추가.
#     (매처는 title+summary를 lowercase 후 매칭한다고 가정. 영문은 단어경계 매칭 권장.)
# ============================================================================

# ---------------------------------------------------------------------------
# 🌱 임팩트  (사용자 확인: 현행 유지)
# ---------------------------------------------------------------------------
IMPACT_KW = [
    "기후리스크", "기후테크", "기후테크 스타트업", "돌봄", "사회적가치",
    "소셜임팩트", "순환경제", "시니어", "신재생에너지", "재생에너지",
    "태양광", "풍력", "해상풍력", "ess", "에너지저장", "전력수요",
    "데이터센터 전력", "탈탄소", "에너지전환", "esg 공시", "esg 금융",
    "녹색채권", "녹색펀드", "임팩트투자", "임팩트펀드", "소셜벤처",         # ➕임팩트펀드/소셜벤처
    "탄소국경세", "탄소중립", "탄소상쇄", "친환경", "물 리스크", "폐수",
    "자원재활용", "열분해", "cbam", "규제샌드박스", "기후부",
    "carbon", "carbon border", "carbon offset", "circular economy",
    "clean energy", "climate risk", "climate tech", "decarbonization",
    "elderly care", "emission", "energy storage", "energy transition",
    "esg", "esg disclosure", "green bond", "green tech", "impact fund",
    "impact investing", "offshore wind", "renewable", "renewable energy",
    "senior care", "social impact", "social venture", "solar",
    "sustainability", "wind power", "water risk",
]

# ---------------------------------------------------------------------------
# 💼 대체투자 (AC / VC / PE)  — ★이번 확장 초점
# ---------------------------------------------------------------------------
ALT_KW = [
    # (a) 단계/라운드
    "프리시드", "시드", "시리즈a", "시리즈b", "시리즈c", "시리즈d",
    "브릿지투자", "후속투자", "프리ipo", "그로스투자",
    "pre-seed", "seed round", "series a", "series b", "series c", "series d",
    "bridge round", "growth equity", "late stage", "pre-ipo", "follow-on",
    # (b) 딜/증권 구조
    "전환사채", "전환우선주", "상환전환우선주", "rcps", "구주매각", "세컨더리",
    "convertible note", "safe note", "secondary", "take-private",
    "carve-out", "카브아웃", "볼트온", "add-on", "메자닌", "mezzanine",
    # (c) 펀드 / LP-GP
    "펀드결성", "펀드클로징", "결성총회", "출자사업", "위탁운용사", "앵커lp",
    "gp커밋", "드라이파우더", "모태펀드", "한국벤처투자", "한국성장금융",
    "개인투자조합", "벤처투자조합", "신기술투자조합", "창투사", "정책펀드",
    "fund of funds", "limited partner", "general partner", "dry powder",
    "capital call", "first close", "final close", "anchor lp",
    # (d) 회수 / 성과지표
    "기업공개", "상장", "인수합병", "경영권인수", "바이아웃", "회수", "엑시트",
    "청산", "리캡", "배당재원회수",
    "ipo", "m&a", "buyout", "lbo", "leveraged buyout", "exit", "trade sale",
    "dividend recap", "continuation fund", "irr", "moic", "dpi", "tvpi",
    # (e) AC / 초기투자
    "액셀러레이터", "인큐베이터", "데모데이", "초기투자", "보육", "팁스", "tips",
    "스케일업", "마이크로vc", "엔젤투자",
    "accelerator", "incubator", "demo day", "scale-up", "micro vc",
    "angel investor",
    # (f) 시장 시그널
    "유니콘", "데카콘", "다운라운드", "메가라운드", "투자혹한기", "밸류에이션",
    "자금조달", "투자유치", "펀딩",
    "unicorn", "decacorn", "down round", "mega round", "funding winter",
    "valuation", "fundraising", "deal flow", "funding round",
    # (g) 국내 VC 촉진 제도
    "벤처투자촉진법", "벤처펀드", "신기사",
]

# ---------------------------------------------------------------------------
# 🤖 AI  — ★이번 확장 초점
# ---------------------------------------------------------------------------
AI_KW = [
    # (a) 모델 / 기술
    "거대언어모델", "생성형 ai", "파운데이션모델", "프론티어모델", "멀티모달",
    "추론모델", "파인튜닝", "오픈소스 ai", "온디바이스 ai", "sllm",
    "llm", "foundation model", "frontier model", "multimodal", "reasoning model",
    "fine-tuning", "rag", "inference", "open weight", "open source ai",
    "small language model", "mixture of experts", "distillation",
    # (b) 에이전트
    "ai 에이전트", "에이전틱 ai", "자율에이전트", "컴퓨터유즈",
    "ai agent", "agentic ai", "autonomous agent", "tool use", "computer use",
    # (c) 칩 / 인프라
    "ai 반도체", "ai 가속기", "gpu", "npu", "hbm", "데이터센터", "ai 데이터센터",
    "하이퍼스케일러", "추론칩", "온디바이스", "ai 인프라",
    "ai chip", "ai accelerator", "tpu", "datacenter", "hyperscaler", "cuda",
    "cowos", "inference chip", "ai infrastructure",
    # (d) 투자 / 시장
    "ai capex", "ai 투자", "ai 버블", "ai 밸류에이션", "ai 스타트업",
    "컴퓨팅투자", "설비투자", "자본지출", "ai 수익화",
    "ai bubble", "ai valuation", "ai startup", "enterprise ai",
    "ai monetization", "capex",
    # (e) 규제 / 정책
    "ai 규제", "ai 기본법", "ai 안전", "수출규제", "반도체 수출규제",
    "ai act", "ai regulation", "ai safety", "export control",
    "chip export control", "ai alignment",
    # (f) 응용 / 임팩트 교차
    "ai 신약", "ai 헬스케어", "로보틱스", "휴머노이드", "자율주행", "기후 ai",
    "ai drug discovery", "robotics", "humanoid", "autonomous driving", "climate ai",
    # (g) 핵심 플레이어(범용어와 겹치지 않는 것만; 나머지는 WATCHLIST_AI)
    "엔비디아", "인공지능", "머신러닝", "딥러닝", "반도체", "파운드리",
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "gpt", "generative ai", "nvidia", "semiconductor", "foundry",
]

# ---------------------------------------------------------------------------
# 🌐 거시·정책·지정학  (📊 시트도출 — 유지)
# ---------------------------------------------------------------------------
MACRO_KW = [
    "거시경제", "경기침체", "관세", "상호관세", "보편관세", "반도체 관세",
    "철강 관세", "감세", "세제개편", "상호교역법", "국채금리", "모기지금리",
    "금리", "기준금리", "무역갈등", "보호무역", "소비자물가", "pce", "생산자물가",
    "고용지표", "실업률", "비농업", "유동성", "인플레이션", "점도표", "통화정책",
    "환율", "지정학", "지정학 리스크", "국제유가", "두바이유", "달러인덱스",
    "소매판매", "부동산", "수출입", "ira", "chips법", "배터리", "2차전지",
    "bond yield", "brent", "central bank", "cpi", "dollar index", "dxy",
    "economic growth", "exchange rate", "fed", "federal reserve", "fomc",
    "geopolitical", "geopolitical risk", "gdp", "inflation", "interest rate",
    "krw", "liquidity", "macroeconomy", "monetary policy", "mortgage rate",
    "oil price", "ppi", "protectionism", "recession", "retail sales",
    "tariff", "trade war", "unemployment", "usd", "wti"
]
# ---------------------------------------------------------------------------
# 👔 MBB·Big4 인사이트
# ---------------------------------------------------------------------------
INSIGHTS_KW = [
    "mckinsey", "맥킨지", "bcg", "bain", "베인", "deloitte", "딜로이트",
    "pwc", "ey", "kpmg", "sloan", "harvard business", "hbr", "insights",
    "strategy+business", "executive", "ceo survey", "megatrend", "메가트렌드",
    "백서", "whitepaper", "outlook", "survey", "report"
]
# ---------------------------------------------------------------------------
# 카테고리(분류) = 위 리스트 그대로. 수집필터는 자동 생성 → 어긋남 없음.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 👔 인사이트 (MBB / Big4)  — ★5번째 카테고리 (주로 '출처' 기반으로 배정됨)
#   키워드로도 최소 포착하되, 실제 배정은 INSIGHT_SOURCES/센더 오버라이드가 주도.
# ---------------------------------------------------------------------------
INSIGHT_KW = [
    "management consulting", "corporate strategy", "executive perspective",
    "thought leadership", "경영전략", "컨설팅 인사이트", "산업 리포트",
    "mckinsey", "bcg", "bain", "deloitte", "kpmg", "strategy+business",
]

CATEGORIES = {
    "🌱 임팩트": IMPACT_KW,
    "🤖 AI": AI_KW,
    "💼 대체투자": ALT_KW,
    "🌐 거시·정책·지정학": MACRO_KW,
    "👔 MBB·Big4 인사이트": INSIGHT_KW,
}

# 해외 도메인 가점에도 추가 (영어 보고서 가점을 위해)
OVERSEAS_PREFERRED_DOMAINS = ["🌱 임팩트", "🤖 AI", "💼 대체투자", "👔 MBB·Big4 인사이트"]


INTEREST_KEYWORDS = sorted(set(k for kws in CATEGORIES.values() for k in kws))

# 인사이트로 '출처 기반' 강제 배정할 소스/센더 (키워드 무관)
INSIGHT_SOURCES = {
    "McKinsey Insights", "PwC strategy+business", "MBB/Big4 insights",
    "MIT Sloan Management",
}
INSIGHT_SENDER_HINTS = [   # 뉴스레터 발신자/제목에 이게 있으면 인사이트로
    "mckinsey", "bcg", "boston consulting", "bain", "deloitte", "kpmg",
    "pwc", "strategy+business", "ey ", "ernst", "sloan",
]

def is_insight_source(name: str) -> bool:
    if not name:
        return False
    if name in INSIGHT_SOURCES:
        return True
    low = name.lower()
    return any(h in low for h in INSIGHT_SENDER_HINTS)

# ---------------------------------------------------------------------------
# 인물·기관 워치리스트 (강신호 — 매처에서 WATCHLIST_WEIGHT 가중치 권장)
# ---------------------------------------------------------------------------
# 거시/정책 (📊시트)
WATCHLIST_MACRO = [
    "트럼프", "trump", "파월", "powell", "워시", "warsh", "베센트", "bessent",
    "연준", "연준 의장", "fed", "fomc", "한국은행", "한은", "이창용",
    "기후부", "기후에너지환경부", "ecb", "유럽중앙은행", "wto", "imf",
    "ira", "chips법", "칩스법",
]
# 대체투자 — 글로벌 + 국내 + 임팩트 전문 (❓유지보수 필요: 상황 따라 갱신)
WATCHLIST_VC_PE = [
    # 글로벌 VC/PE
    "sequoia", "a16z", "andreessen", "accel", "tiger global", "softbank",
    "general catalyst", "lightspeed", "bessemer", "blackstone", "kkr",
    "carlyle", "apollo", "tpg rise", "generation im",
    # 국내 VC/PE
    "카카오벤처스", "한국투자파트너스", "알토스벤처스", "sbva", "소프트뱅크벤처스",
    "스톤브릿지", "캡스톤파트너스", "본엔젤스", "프라이머", "dsc인베스트먼트",
    "에이티넘", "imm", "스틱", "프리미어파트너스",
    # 국내 임팩트 전문
    "소풍벤처스", "옐로우독", "인비저닝파트너스", "임팩트스퀘어", "hgi", "디쓰리쥬빌리",
]
# AI 랩/기업 (범용어 겹침 없는 고유명만; ❓유지보수 필요)
WATCHLIST_AI = [
    "openai", "오픈ai", "anthropic", "앤스로픽", "deepmind", "딥마인드",
    "mistral", "xai", "grok", "cohere", "perplexity", "퍼플렉시티",
    "deepseek", "딥시크", "scale ai", "hugging face", "허깅페이스",
    "tsmc", "asml", "arm",
    # 국내 AI/AI칩 스타트업(투자 대상)
    "업스테이지", "뤼튼", "리벨리온", "퓨리오사", "사피온", "하이퍼클로바",
]

# ---------------------------------------------------------------------------
# 교차 태그 — 두 축이 겹치는 기사 라벨링(선택)
# ---------------------------------------------------------------------------
INTERSECTION_TAGS = {
    "AI×에너지/임팩트": [["ai", "데이터센터", "gpu", "nvidia", "전력수요"],
                        ["재생에너지", "전력", "ess", "에너지", "탄소"]],
    "AI×대체투자":      [["ai", "생성형", "llm", "반도체"],
                        ["투자유치", "펀딩", "series", "라운드", "밸류에이션"]],
    "정책리스크×산업":   [["트럼프", "관세", "ira", "chips", "보조금", "수출규제"],
                        ["배터리", "반도체", "2차전지", "자동차", "ai"]],
}

# ---------------------------------------------------------------------------
# 블랙리스트 (원하는 기사 죽이던 항목 제거됨)
# ---------------------------------------------------------------------------
BLACKLIST_KEYWORDS = [
    "coupon", "promo code", "discount code", "% off",
    "best deals", "best price", "buy now", "airdoctor", "booking.com",
    "best laptop", "laptop review",
    "celebrity", "sports", "entertainment", "gaming", "movie", "tv show", "gossip",
    "github repo", "code walkthrough",
    "배임", "횡령", "파업",
]
SOFT_PENALTY_KEYWORDS = [
    "논란", "의혹", "고발", "제련소",
    # 소비자/how-to 노이즈(임팩트 피드의 DIY·구매가이드류 걸러내기)
    "diy", "on a budget", "gift guide", "buying guide", "buyer's guide",
    "best portable", "hands-on",
]

# ---------------------------------------------------------------------------
# RSS 소스 (name -> url)  ※ 기존 로더 호환 위해 dict 유지
#  ★ 사용자 지정: 임팩트/AI/대체투자는 '해외 비중↑' → 해외 소스 대폭 추가 +
#     SOURCE_META의 region/weight로 랭킹 가점(아래). ✅=피드 확인, ❓=실사용 전 URL 확인
# ---------------------------------------------------------------------------
RSS_SOURCES = {
    # ── 🌍 해외 임팩트 / 기후 ──
    "ImpactAlpha": "https://impactalpha.com/feed/",                  # ✅
    "ESG Today": "https://www.esgtoday.com/feed/",                   # ✅
    "Trellis (구 GreenBiz)": "https://trellis.net/feed/",            # ❓
    "Canary Media": "https://www.canarymedia.com/rss",              # ❓
    "ESG Dive": "https://www.esgdive.com/feeds/news/",              # ❓
    # ── 🌍 해외 AI ──
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",  # ❓
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",  # ❓
    "MIT Tech Review": "https://www.technologyreview.com/feed/",     # ✅
    "The Batch (deeplearning.ai)": "https://www.deeplearning.ai/the-batch/feed/",      # ❓
    "Import AI (J. Clark)": "https://jack-clark.net/feed/",         # ❓
    "SemiAnalysis (칩/인프라)": "https://www.semianalysis.com/feed", # ❓
    # ── 🌍 해외 VC / PE / 스타트업 ──
    "TechCrunch": "https://techcrunch.com/feed/",                   # ✅
    "TechCrunch Venture": "https://techcrunch.com/category/venture/feed/",  # ❓
    "Sifted (EU 스타트업)": "https://sifted.eu/feed",               # ❓
    "Crunchbase News": "https://news.crunchbase.com/feed/",         # ❓
    "Wired": "https://www.wired.com/feed/rss",                      # ✅
    # ── 👔 MBB / Big4 (인사이트) ── native RSS 있는 곳만. 나머지는 GENERATED/NEWSLETTER
    "McKinsey Insights": "https://www.mckinsey.com/insights/rss",   # ✅ native 확인
    "PwC strategy+business": "https://www.strategy-business.com/rss",  # ✅ native(저빈도)
    "MIT Sloan Management": "https://sloanreview.mit.edu/feed/",     # ✅
    # ── 🇰🇷 국내 (보조 — 매크로/국내딜용, 위 도메인에선 가중치 낮음) ──
    "ImpactOn (임팩트온)": "http://www.impacton.net/rss/allArticle.xml",  # 📊 국내 임팩트 최다
    "Platum (플랫텀)": "https://platum.kr/feed",
    "VentureSquare (벤처스퀘어)": "https://www.venturesquare.net/feed",
    "한경 Geeks (벤처/VC)": "https://rss.hankyung.com/feed/geeks.xml",
    "전자신문 (벤처/스타트업)": "https://rss.etnews.com/Section902.xml",
}

# ── 지역/도메인 가중치 : 임팩트·AI·대체투자 기사에 한해 '해외 소스' 가점 ──
OVERSEAS_PREFERRED_DOMAINS = ["🌱 임팩트", "🤖 AI", "💼 대체투자", "👔 인사이트"]  # ➕ 사용자 지정
KR_SOURCES = {                                                       # 국내 소스만 명시(나머지 global)
    "ImpactOn (임팩트온)", "Platum (플랫텀)", "VentureSquare (벤처스퀘어)",
    "한경 Geeks (벤처/VC)", "전자신문 (벤처/스타트업)",
}
REGION_WEIGHT = {"global": 1.35, "kr": 1.0}      # 매처: 기사 카테고리가 위 도메인이고 소스=global → score *= 1.35
MIN_OVERSEAS_RATIO = 0.6                          # 위 도메인의 카테고리 상한 채울 때 해외 최소 비율(예약)

def source_region(name):                          # ➕ 헬퍼: 소스 지역 반환
    return "kr" if name in KR_SOURCES else "global"

# ---------------------------------------------------------------------------
# 👔 MBB/Big4 & 뉴스레터·카드뉴스 : native RSS가 없는 소스 처리법
# ---------------------------------------------------------------------------
# (A) 인사이트 페이지 → RSS 변환기(RSS.app / FetchRSS / Feeder.co)로 피드 생성 후 붙여넣기.
#     BCG·Bain·Deloitte·EY·KPMG는 네이티브 RSS가 없어 이 방식이 사실상 표준.
GENERATED_FEEDS = {
    # "BCG Featured Insights": "<RSS.app 등에서 https://www.bcg.com/publications 변환>",
    # "Bain Insights":         "<변환 URL: https://www.bain.com/insights/>",
    # "Deloitte Insights":     "<변환 URL>  또는  https://blogs.deloitte.co.uk/feed 부분대체",
    # "EY Insights":           "<변환 URL: https://www.ey.com/en_gl/insights>",
    # "KPMG Insights":         "<변환 URL: https://kpmg.com/xx/en/home/insights.html>",
}
# (B) 이메일 뉴스레터 → 이메일-투-RSS 브릿지(kill-the-newsletter.com 등)로 (수신주소+피드) 생성,
#     뉴스레터를 그 주소로 구독 → 발급된 피드 URL을 아래에. (MBB/Big4 뉴스레터도 이 경로 권장)
NEWSLETTER_FEEDS = {
    # "McKinsey Shortlist":  "<KTN 피드 URL>",
    # "BCG Executive Persp.":"<KTN 피드 URL>",
    # "Deloitte Daily Exec": "<KTN 피드 URL>",
    # "StrictlyVC":          "<KTN 피드 URL>",
    # "Axios Pro Rata":      "<KTN 피드 URL>",
    # "Term Sheet (Fortune)":"<KTN 피드 URL>",
}
# (C) 카드뉴스(인스타/링크드인 비주얼): RSS로 안정 수집 불가.
#     → 텍스트 요약이 목적이면 위 (A)/(B)로 대체, 이미지 자체가 필요하면 수동/별도 스크래퍼(권장X).

# ➕ Google News RSS 쿼리 피드 — 종합매체 가로질러 헤드라인 수집(URL 실사용 전 1회 확인)
_GNEWS = "https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
GOOGLE_NEWS_QUERIES = {
    # 대체투자
    "국내 투자유치": "(시리즈A OR 시리즈B OR 프리IPO) 투자유치",
    "펀드결성/출자": "(벤처펀드 OR 모태펀드) (결성 OR 출자사업)",
    "M&A/회수": "스타트업 (인수 OR M&A OR 상장)",
    "글로벌 VC 라운드": "startup (Series OR funding round OR raises)",
    # AI
    "AI 투자/펀딩": "AI 스타트업 (투자유치 OR 펀딩)",
    "AI 반도체/인프라": "(AI 반도체 OR GPU OR 데이터센터) (엔비디아 OR 투자)",
    "생성형 AI 동향": "(생성형 AI OR LLM OR 에이전트)",
    # 거시/정책(📊)
    "미국 통화정책": "FOMC OR 연준 OR 파월 금리",
    "트럼프 관세/세제": "트럼프 (관세 OR 상호관세 OR 감세)",
    "IRA·반도체 정책": "(IRA OR 칩스법) (배터리 OR 반도체 보조금)",
    "한은 통화정책": "한국은행 (기준금리 OR 환율)",
    # 임팩트
    "임팩트/기후정책": "기후부 OR 재생에너지 OR 녹색채권",
}
GOOGLE_NEWS_FEEDS = {k: _GNEWS.format(q=v) for k, v in GOOGLE_NEWS_QUERIES.items()}

# ➕ 해외(영문) Google News — 임팩트/AI/대체투자 해외 헤드라인 보강
_GNEWS_EN = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
GOOGLE_NEWS_QUERIES_EN = {
    "Global impact/climate": "(impact investing OR climate tech) funding",
    "Global AI funding": "AI startup (raises OR funding round OR valuation)",
    "Global VC/PE deals": "(venture capital OR private equity) (fund OR round OR acquisition)",
    "MBB/Big4 insights": "(McKinsey OR BCG OR Bain OR Deloitte) (AI OR climate OR private equity)",
}
GOOGLE_NEWS_FEEDS.update({k: _GNEWS_EN.format(q=v) for k, v in GOOGLE_NEWS_QUERIES_EN.items()})

# ── 키워드 자동 업데이트 훅 ──────────────────────────────────────────────
# weekly_keywords.json 이 있으면 그 안의 트렌드 용어를 Google News 쿼리에 OR로 끼워
# 새 피드를 자동 생성한다. (주 1회 잡이 이 JSON을 갱신 → 코드 수정 없이 반영)
#   형식: {"트럼프 관세": ["보편관세","IEEPA"], "AI 반도체": ["HBM4","CoWoS"]}
import json as _json, os as _os
def _load_trend_feeds():
    path = _os.path.join(_os.path.dirname(__file__), "weekly_keywords.json")
    if not _os.path.exists(path):
        return {}
    try:
        data = _json.load(open(path, encoding="utf-8"))
    except Exception:
        return {}
    feeds = {}
    for anchor_kw, terms in (data or {}).items():
        if anchor_kw.startswith("_"):
            continue
        terms = [t for t in (terms or []) if t]
        if not terms:
            continue
        q = f"{anchor_kw} (" + " OR ".join(terms) + ")"
        feeds[f"trend:{anchor_kw}"] = _GNEWS.format(q=q)
    return feeds
GOOGLE_NEWS_FEEDS.update(_load_trend_feeds())

# ── 러너용 통합 피드(원하면 이걸로 일괄 순회) ──
ALL_FEEDS = {**RSS_SOURCES, **GENERATED_FEEDS, **NEWSLETTER_FEEDS, **GOOGLE_NEWS_FEEDS}

# ---------------------------------------------------------------------------
# Hacker News 검색어
# ---------------------------------------------------------------------------
HN_KEYWORDS = [
    # AI
    "AI funding", "AI capex", "AI datacenter", "foundation model", "AI agent",
    "Nvidia", "inference", "LLM", "AI valuation",
    # 대체투자
    "venture capital", "private equity", "startup funding", "Series A", "down round",
    # 임팩트/거시
    "climate tech", "ESG", "inflation", "federal reserve", "tariff", "export control",
]

# ---------------------------------------------------------------------------
# 설정 옵션
# ---------------------------------------------------------------------------
SIMILARITY_THRESHOLD = 0.75      # ❓용도 확인(중복제거 vs 관련도게이트)
MAX_ARTICLES_PER_RUN = 24        # ✅ AI/대체투자 축 늘어난 만큼 상향
MAX_PER_CATEGORY = 7             # ➕ 카테고리별 상한
RECENCY_HOURS = 36

# LLM 리랭크 사용 시(GEMINI_API_KEY 있을 때)만 적용되는 발송 임계점수(0=끄기).
# 예: 80 이면 llm_score 80점 미만은 발송 제외. 규칙 랭킹만 쓸 땐 무시됨.
LLM_SEND_MIN_SCORE = 0

# ---------------------------------------------------------------------------
# 매처 권장 가드 (config만으론 미적용 — 매처 코드에 반영 권장)
# ---------------------------------------------------------------------------
# - 영문: 단어경계 r"\b"+re.escape(kw)+r"\b", re.IGNORECASE
#   (특히 이번 확장의 짧은 토큰: gpu/npu/tpu/rag/exit/safe note/lbo/irr/dpi/xai/arm)
# - 약어는 대소문자 유지 경계매칭
# - 점수 = Σ(카테고리 히트) + Σ(WATCHLIST 히트 × WATCHLIST_WEIGHT) − Σ(SOFT_PENALTY)
#   채택: 점수 ≥ 임계 AND BLACKLIST 0 AND CATEGORIES 최소1개
MATCH_WORD_BOUNDARY = True
WATCHLIST_WEIGHT = 2.0
ALL_WATCHLISTS = WATCHLIST_MACRO + WATCHLIST_VC_PE + WATCHLIST_AI
ACRONYM_KEYWORDS = ["AI", "M&A", "IPO", "CPI", "PCE", "PPI", "HBM", "GPU", "TPU",
                    "NPU", "RAG", "LBO", "IRR", "MOIC", "DPI", "TVPI", "DXY",
                    "IRA", "GDP", "FOMC", "ESS", "ECB", "WTO", "RCPS", "SBVA"]
