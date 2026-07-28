import os

# ---------------------------------------------------------------------------
# 🤖 제미나이 모델명 빈칸 자동 방어 로직
# ---------------------------------------------------------------------------
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
if not GEMINI_MODEL or GEMINI_MODEL.strip() == "":
    os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"
    GEMINI_MODEL = "gemini-1.5-flash"

# ---------------------------------------------------------------------------
# 1. 관심 키워드 (이 단어가 있어야 최종 선택됨)
# ---------------------------------------------------------------------------
IMPACT_KW = [
    "impact investing", "climate tech", "carbon neutral", "net zero",
    "energy transition", "renewable energy", "esg", "sustainability",
    "green fund", "climate fund", "임팩트투자", "기후테크", "탄소중립",
    "넷제로", "에너지전환", "재생에너지", "지속가능", "녹색기금", "기후펀드",
    "사회적기업", "소셜벤처", "그린뉴딜", "클린테크", "순환경제",
]

AI_KW = [
    "artificial intelligence", "generative ai", "llm", "large language model",
    "gpt", "claude", "gemini", "openai", "anthropic", "deepmind",
    "ai startup", "ai investment", "ai fund", "ai chip", "gpu",
    "ai agent", "autonomous agent", "copilot", "multimodal",
    "인공지능", "생성형", "거대언어모델", "에이전트", "ai 반도체", "엔비디아",
]

ALT_KW = [
    "private equity", "venture capital", "private debt", "private credit",
    "infrastructure fund", "real estate fund", "secondary fund", "buyout",
    "growth equity", "fund of funds", "lp", "gp", "dry powder",
    "대체투자", "사모펀드", "벤처캐피탈", "사모채권", "인프라펀드",
    "부동산펀드", "세컨더리", "바이아웃", "그로스에쿼티", "출자자",
    "운용사", "드라이파우더", "블라인드펀드", "모태펀드", "공제회", "스타트업",
]

MACRO_KW = [
    "fomc", "federal reserve", "interest rate", "inflation", "cpi",
    "gdp", "recession", "soft landing", "geopolitics", "tariff",
    "trade war", "supply chain", "sanctions", "oil price", "opec",
    "기준금리", "인플레이션", "물가상승", "경기침체", "연준", "한국은행",
    "지정학", "관세", "무역전쟁", "공급망", "제재", "유가", "환율",
    "미중갈등", "중동", "우크라이나", "대만",
]

INSIGHTS_KW = [
    "mckinsey", "맥킨지", "bcg", "bain", "베인", "deloitte", "딜로이트",
    "pwc", "ey", "kpmg", "sloan", "harvard business", "hbr", "insights",
    "strategy+business", "executive", "ceo survey", "megatrend", "메가트렌드",
    "백서", "whitepaper", "outlook", "survey", "report"
]

INTEREST_KEYWORDS = sorted(set(IMPACT_KW + AI_KW + ALT_KW + MACRO_KW + INSIGHTS_KW))
HN_KEYWORDS = INTEREST_KEYWORDS

# ---------------------------------------------------------------------------
# 2. 카테고리 및 발송/점수 설정 (🚀 누락된 변수 완벽 보강!)
# ---------------------------------------------------------------------------
CATEGORIES = {
    "🌱 임팩트": IMPACT_KW,
    "🤖 AI": AI_KW,
    "💼 대체투자": ALT_KW,
    "🌐 거시·정책·지정학": MACRO_KW,
    "👔 MBB·Big4 인사이트": INSIGHTS_KW,
}

OVERSEAS_PREFERRED_DOMAINS = ["🌱 임팩트", "🤖 AI", "💼 대체투자", "👔 MBB·Big4 인사이트"]
REGION_WEIGHT = {"global": 1.35, "korea": 1.0}
MAX_PER_CATEGORY = 4
LLM_SEND_MIN_SCORE = 0       # LLM 편집장이 자율 판단하도록 0으로 설정

# 🚨 [여기서 에러가 났던 것입니다!] 모듈들이 찾는 점수/중복 판단 가중치 변수
SIMILARITY_THRESHOLD = 0.85  # deduplicator.py 용 (중복 기사 병합 기준)
WATCHLIST_WEIGHT = 1.2       # summarizer.py 용 (주요 관심기업 가중치)
SOFT_PENALTY_KEYWORDS = [    # summarizer.py 용 (단순 주가/특징주 기사 감점)
    "특징주", "목표가", "상한가", "하한가", "종목추천", "리딩", "주가전망"
]

# ---------------------------------------------------------------------------
# 3. 블랙리스트 (지자체·소상공인 노이즈 철저 차단!)
# ---------------------------------------------------------------------------
BLACKLIST_KEYWORDS = [
    "coupon", "promo code", "discount code", "% off", "best deals",
    "best price", "buy now", "airdoctor", "booking.com", "best laptop",
    "laptop review", "celebrity", "sports", "entertainment", "gaming",
    "movie", "tv show", "gossip", "github repo", "code walkthrough",
    "배임", "횡령", "파업",
    "중기자금", "소상공인", "지역화폐", "테크노파크", "지자체",
    "인천시", "서울시", "경기도", "부산시", "대구시", "광주시", "대전시", "울산시",
    "경남도", "경북도", "전남도", "전북도", "충남도", "충북도", "강원도", "제주도",
    "특례보증", "육성자금", "이차보전", "도청", "시청"
]

# ---------------------------------------------------------------------------
# 4. RSS 피드 (🚀 ALL_FEEDS / RSS_FEEDS 이름 완벽 호환!)
# ---------------------------------------------------------------------------
ALL_FEEDS = {
    "ImpactAlpha": "https://impactalpha.com/feed/",
    "ESG Today": "https://www.esgtoday.com/feed/",
    "TechCrunch (AI)": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat (AI)": "https://venturebeat.com/category/ai/feed/",
    "The Batch (deeplearning.ai)": "https://www.deeplearning.ai/the-batch/tag/issue/rss/",
    "SemiAnalysis (칩/인프라)": "https://www.semianalysis.com/feed",
    "TechCrunch (Venture)": "https://techcrunch.com/category/venture/feed/",
    "Sifted (EU 스타트업)": "https://sifted.eu/feed",
    "Crunchbase News": "https://news.crunchbase.com/feed/",
    "McKinsey Insights": "https://www.mckinsey.com/insights/rss",
    "BCG Perspectives": "https://www.bcg.com/rss/perspectives.xml",
    "PwC strategy+business": "https://www.strategy-business.com/rss",
    "ImpactOn (임팩트온)": "https://www.impacton.net/rss/allArticle.xml",
    "Platum (플랫텀)": "https://platum.kr/feed",
    "VentureSquare (벤처스퀘어)": "https://www.venturesquare.net/feed",
    "한경 Geeks (벤처/VC)": "https://rss.hankyung.com/feed/geeks.xml",
    "전자신문 (벤처/스타트업)": "https://rss.etnews.com/Section902.xml",
}
RSS_FEEDS = ALL_FEEDS
RSS_SOURCES = ALL_FEEDS

# ---------------------------------------------------------------------------
# 5. 구글 뉴스 (🚀 한경/매경/로이터 등 1군 언론사 속보만 핀셋 수집!)
# ---------------------------------------------------------------------------
GOOGLE_NEWS_FEEDS = {
    "국내 벤처/스타트업": "https://news.google.com/rss/search?q=(%ED%88%AC%EC%9E%90%EC%9C%A0%EC%B9%98+%ED%8E%80%EB%94%A9+M%26A+OR+%EC%8B%9C%EB%A6%AC%EC%A6%88)+when:1d+(source:%ED%95%9C%EA%B5%AD%EA%B5%BF%EC%A0%9C+OR+source:%EB%A7%A4%EC%9D%BC%EA%B5%BF%EC%A0%9C+OR+source:%EC%A0%84%EC%9E%90%EC%8B%A0%EB%AC%B8)&hl=ko&gl=KR&ceid=KR:ko",
    "글로벌 AI/매크로": "https://news.google.com/rss/search?q=(AI+OR+FOMC+OR+interest+rate+OR+tariff)+when:1d+(source:Bloomberg+OR+source:Reuters+OR+source:Financial+Times)&hl=en-US&gl=US&ceid=US:en",
    "MBB/Big4 인사이트": "https://news.google.com/rss/search?q=(McKinsey+OR+BCG+OR+Bain+OR+Deloitte)+(AI+OR+climate+OR+private+equity)&hl=en-US&gl=US&ceid=US:en"
}
