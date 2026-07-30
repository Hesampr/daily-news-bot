import os

# ---------------------------------------------------------------------------
# 🤖 제미나이 모델명 빈칸 자동 방어 로직
# ---------------------------------------------------------------------------
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
if not GEMINI_MODEL or GEMINI_MODEL.strip() == "":
    os.environ["GEMINI_MODEL"] = "gemini-2.0-flash"
    GEMINI_MODEL = "gemini-2.0-flash"

# ---------------------------------------------------------------------------
# 1. 관심 키워드 (🚀 최신 AI 모델명, VC 펀딩 단계, 매크로 지표 완벽 확장!)
# ---------------------------------------------------------------------------
IMPACT_KW = [
    "impact investing", "climate tech", "carbon neutral", "net zero",
    "energy transition", "renewable energy", "esg", "sustainability",
    "green fund", "climate fund", "cleantech", "decarbonization", "ev infrastructure",
    "임팩트투자", "기후테크", "탄소중립", "넷제로", "에너지전환",
    "재생에너지", "지속가능", "녹색기금", "기후펀드", "사회적기업",
    "소셜벤처", "그린뉴딜", "클린테크", "순환경제", "이차전지"
]

AI_KW = [
    "artificial intelligence", "generative ai", "llm", "large language model",
    "gpt", "gpt-4o", "gpt-5", "o3", "o4-mini", "claude", "claude sonnet", "claude opus",
    "gemini", "gemini 2.0", "gemini 2.5", "openai", "anthropic", "deepmind",
    "grok", "deepseek", "mistral", "qwen", "kimi", "cursor", "windsurf", "codex",
    "ai startup", "ai investment", "ai fund", "ai chip", "gpu", "semiconductor",
    "ai agent", "autonomous agent", "copilot", "multimodal", "data center",
    "인공지능", "생성형", "거대언어모델", "에이전트", "ai 반도체", "엔비디아", "데이터센터"
]

ALT_KW = [
    "private equity", "venture capital", "private debt", "private credit",
    "infrastructure fund", "real estate fund", "secondary fund", "buyout",
    "growth equity", "fund of funds", "lp", "gp", "dry powder",
    "series a", "series b", "series c", "series d", "series e",
    "seed round", "pre-seed", "growth round", "bridge round", "late stage",
    "fundraising", "vc funding", "unicorn", "ipo", "pre-ipo", "valuation",
    "exit", "take private", "continuation fund", "buy and build",
    "대체투자", "사모펀드", "벤처캐피탈", "사모채권", "인프라펀드",
    "부동산펀드", "세컨더리", "바이아웃", "그로스에쿼티", "출자자",
    "운용사", "드라이파우더", "블라인드펀드", "모태펀드", "공제회",
    "스타트업", "투자유치", "펀딩", "시리즈a", "시리즈b", "프리ipo", "인수", "합병", "유니콘"
]

MACRO_KW = [
    "fomc", "federal reserve", "interest rate", "inflation", "cpi",
    "gdp", "recession", "soft landing", "geopolitics", "tariff",
    "trade war", "supply chain", "sanctions", "oil price", "opec",
    "treasury yield", "10-year treasury", "yield curve", "dot plot",
    "기준금리", "인플레이션", "물가상승", "경기침체", "연준", "한국은행",
    "지정학", "관세", "무역전쟁", "공급망", "제재", "유가", "환율",
    "미중갈등", "중동", "우크라이나", "대만", "통화정책", "금리", "스콧베센트", "트럼", "거시경제"
]

INSIGHTS_KW = [
    "mckinsey", "맥킨지", "bcg", "bain", "베인", "deloitte", "딜로이트",
    "pwc", "ey", "kpmg", "sloan", "harvard business", "hbr", "insights",
    "strategy+business", "executive", "ceo survey", "megatrend", "메가트렌드",
    "whitepaper", "outlook", "survey", "report", "strategic framework",
    "보고서", "전망", "조사", "컨설팅", "트렌드", "인사이트", "산업동향"
]

INTEREST_KEYWORDS = sorted(set(IMPACT_KW + AI_KW + ALT_KW + MACRO_KW + INSIGHTS_KW))
HN_KEYWORDS = INTEREST_KEYWORDS

# ---------------------------------------------------------------------------
# 2. 카테고리 및 발송/점수 설정
# ---------------------------------------------------------------------------
CATEGORIES = {
    "🌱 임팩트": IMPACT_KW,
    "🤖 AI": AI_KW,
    "💼 대체투자": ALT_KW,
    "🌐 거시·정책·지정학": MACRO_KW,
    "👔 MBB·Big4 인사이트": INSIGHTS_KW,
}

MAX_PER_CATEGORY_DICT = {
    "🌱 임팩트": 4,
    "🤖 AI": 4,
    "💼 대체투자": 4,
    "🌐 거시·정책·지정학": 4,
    "👔 MBB·Big4 인사이트": 2,  # 핵심 인사이트는 엄선하여 2개만 발송
}
MAX_PER_CATEGORY = 4

OVERSEAS_PREFERRED_DOMAINS = ["🌱 임팩트", "🤖 AI", "💼 대체투자", "👔 MBB·Big4 인사이트"]
REGION_WEIGHT = {"global": 1.35, "korea": 1.0}
LLM_SEND_MIN_SCORE = 0

SIMILARITY_THRESHOLD = 0.85
WATCHLIST_WEIGHT = 2.5       # 관심기업 존재감 극대화
SOFT_PENALTY_KEYWORDS = [
    "특징주", "목표가", "상한가", "하한가", "종목추천", "리딩", "주가전망"
]

# ---------------------------------------------------------------------------
# 3. 블랙리스트 (지자체·소상공인·가십 철저 차단)
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
# 4. 중앙 통제식 RSS 피드 메타데이터 (Tier 및 Priority 완벽 적용)
# - Primary (우선순위 5) : 무조건 최우선 검토되는 A급 핵심 출처
# - Supplemental (우선순위 3~4) : 보조 출처 (LLM 후보군으로 주로 활용)
# ---------------------------------------------------------------------------
RSS_SOURCE_METADATA = {
    # 🌱 임팩트 (가장 중요 -> A급 매체 최대 포진)
    "Impact Alpha": {"url": "https://impactalpha.com/feed/", "category": "🌱 임팩트", "tier": "primary", "priority": 5},
    "NextBillion": {"url": "https://nextbillion.net/feed/", "category": "🌱 임팩트", "tier": "primary", "priority": 5},
    "SSIR": {"url": "https://ssir.org/site/rss_2.0/", "category": "🌱 임팩트", "tier": "primary", "priority": 5},
    "Pioneers Post": {"url": "https://www.pioneerspost.com/rss.xml", "category": "🌱 임팩트", "tier": "primary", "priority": 5},
    "Carbon Brief": {"url": "https://www.carbonbrief.org/feed/", "category": "🌱 임팩트", "tier": "primary", "priority": 5},
    "Responsible Investor": {"url": "https://www.responsible-investor.com/feed/", "category": "🌱 임팩트", "tier": "primary", "priority": 5},
    "ImpactOn (임팩트온)": {"url": "https://www.impacton.net/rss/allArticle.xml", "category": "🌱 임팩트", "tier": "supplemental", "priority": 4},
    "Canary Media": {"url": "https://www.canarymedia.com/rss", "category": "🌱 임팩트", "tier": "supplemental", "priority": 4},
    "Climate Home News": {"url": "https://www.climatechangenews.com/feed/", "category": "🌱 임팩트", "tier": "supplemental", "priority": 4},

    # 🤖 AI (투자/규제/인프라 관점)
    "TechCrunch AI": {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "🤖 AI", "tier": "primary", "priority": 5},
    "MIT Tech Review (AI)": {"url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "category": "🤖 AI", "tier": "primary", "priority": 5},
    "SemiAnalysis": {"url": "https://www.semianalysis.com/feed", "category": "🤖 AI", "tier": "primary", "priority": 5},
    "The Batch": {"url": "https://www.deeplearning.ai/the-batch/tag/issue/rss/", "category": "🤖 AI", "tier": "primary", "priority": 5},
    "The Verge AI": {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "🤖 AI", "tier": "supplemental", "priority": 3},
    "Ars Technica": {"url": "https://feeds.arstechnica.com/arstechnica/index", "category": "🤖 AI", "tier": "supplemental", "priority": 3},

    # 💼 대체투자 (딜소싱 및 펀드 운용)
    "PitchBook News": {"url": "https://pitchbook.com/rss/news", "category": "💼 대체투자", "tier": "primary", "priority": 5},
    "PE Hub": {"url": "https://www.pehub.com/feed/", "category": "💼 대체투자", "tier": "primary", "priority": 5},
    "Crunchbase News": {"url": "https://news.crunchbase.com/feed/", "category": "💼 대체투자", "tier": "primary", "priority": 5},
    "TechCrunch Venture": {"url": "https://techcrunch.com/category/venture/feed/", "category": "💼 대체투자", "tier": "primary", "priority": 5},
    "VCJ": {"url": "https://venturecapitaljournal.com/feed/", "category": "💼 대체투자", "tier": "primary", "priority": 5},
    "Sifted": {"url": "https://sifted.eu/feed", "category": "💼 대체투자", "tier": "supplemental", "priority": 4},
    "VentureSquare (벤처스퀘어)": {"url": "https://www.venturesquare.net/feed", "category": "💼 대체투자", "tier": "supplemental", "priority": 3},
    "Platum (플랫텀)": {"url": "https://platum.kr/feed", "category": "💼 대체투자", "tier": "supplemental", "priority": 3},
    "한경 Geeks (벤처/VC)": {"url": "https://rss.hankyung.com/feed/geeks.xml", "category": "💼 대체투자", "tier": "supplemental", "priority": 3},

    # 🌐 거시경제·정책·지정학
    "The Economist": {"url": "https://www.economist.com/finance-and-economics/rss.xml", "category": "🌐 거시·정책·지정학", "tier": "primary", "priority": 5},
    "Foreign Affairs": {"url": "https://www.foreignaffairs.com/rss.xml", "category": "🌐 거시·정책·지정학", "tier": "primary", "priority": 5},

    # 👔 MBB·Big4 인사이트
    "McKinsey Insights": {"url": "https://www.mckinsey.com/insights/rss", "category": "👔 MBB·Big4 인사이트", "tier": "primary", "priority": 5},
    "BCG Insights": {"url": "https://www.bcg.com/rss", "category": "👔 MBB·Big4 인사이트", "tier": "primary", "priority": 5},
    "PwC strategy+business": {"url": "https://www.strategy-business.com/rss", "category": "👔 MBB·Big4 인사이트", "tier": "primary", "priority": 5},
}

# 🚀 위 단일 메타데이터에서 수집용 URL 리스트 자동 생성!
ALL_FEEDS = {name: meta["url"] for name, meta in RSS_SOURCE_METADATA.items()}
RSS_FEEDS = ALL_FEEDS
RSS_SOURCES = ALL_FEEDS

# ---------------------------------------------------------------------------
# 5. 구글 뉴스 (🚀 when:3d 유지 & 정교한 AND 검색식 적용)
# ---------------------------------------------------------------------------
# Keep optional ranking inputs explicit. An empty watchlist preserves the
# current ranking behavior while allowing operators to add company or topic
# names without relying on an import fallback in the processor.
ALL_WATCHLISTS = []

# Source names contain localized display text, so derive the Korean-source set
# from stable feed domains rather than duplicating those display names here.
_KOREA_SOURCE_DOMAINS = (
    "impacton.net",
    "platum.kr",
    "venturesquare.net",
    "hankyung.com",
    "etnews.com",
)
KOREA_SOURCE_NAMES = frozenset(
    source_name
    for source_name, feed_url in ALL_FEEDS.items()
    if any(domain in feed_url for domain in _KOREA_SOURCE_DOMAINS)
)


def source_region(source_name: str) -> str:
    """Return the configured region for a known feed source."""
    return "korea" if source_name in KOREA_SOURCE_NAMES else "global"


GOOGLE_NEWS_FEEDS = {
    "국내 VC/스타트업": "https://news.google.com/rss/search?q=(%ED%88%AC%EC%9E%90%EC%9C%A0%EC%B9%98+OR+%ED%8E%80%EB%94%A9+OR+M%26A+OR+%EC%8B%9C%EB%A6%AC%EC%A6%88A+OR+%EC%8B%9C%EB%A6%AC%EC%A6%88B+OR+%EB%B2%A4%EC%B2%98%ED%8E%80%EB%93%9C)+when:3d&hl=ko&gl=KR&ceid=KR:ko",
    "글로벌 VC/PE": "https://news.google.com/rss/search?q=(venture+capital+OR+private+equity+OR+funding+round+OR+dry+powder+OR+startup+raising)+when:3d&hl=en-US&gl=US&ceid=US:en",
    "미국 통화정책/금리": "https://news.google.com/rss/search?q=(FOMC+OR+%EC%97%B0%EC%A4%80+OR+%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC+OR+%ED%8C%8C%EC%9B%94+OR+inflation+OR+treasury+yield)+when:3d&hl=ko&gl=KR&ceid=KR:ko",
    "글로벌 거시/지정학": "https://news.google.com/rss/search?q=(interest+rate+OR+recession+OR+tariff+OR+geopolitics+OR+federal+reserve)+when:3d&hl=en-US&gl=US&ceid=US:en",
    "MBB/Big4 인사이트": "https://news.google.com/rss/search?q=(McKinsey+OR+BCG+OR+Bain+OR+Deloitte)+(AI+OR+climate+OR+venture+OR+private+equity)+when:3d&hl=en-US&gl=US&ceid=US:en"
}

# ---------------------------------------------------------------------------
# 6. 출처 기반 카테고리 강제 고정 (Override)
# 전문 매체는 키워드 검사를 건너뛰고 100% 해당 카테고리로 꽂아버립니다.
# ---------------------------------------------------------------------------
SOURCE_CATEGORY_OVERRIDE = {
    # 🌱 임팩트 (이름 베리에이션 및 추천 15개 매체 모두 포함)
    "ImpactOn": "🌱 임팩트",
    "ImpactOn (임팩트온)": "🌱 임팩트",
    "임팩트온": "🌱 임팩트",
    "Impact Alpha": "🌱 임팩트",
    "NextBillion": "🌱 임팩트",
    "Pioneers Post": "🌱 임팩트",
    "SSIR": "🌱 임팩트",
    "Stanford Social Innovation Review": "🌱 임팩트",
    "Devex": "🌱 임팩트",
    "ESG Today": "🌱 임팩트",
    "Responsible Investor": "🌱 임팩트",
    "Environmental Finance": "🌱 임팩트",
    "Corporate Knights": "🌱 임팩트",
    "Canary Media": "🌱 임팩트",
    "Carbon Brief": "🌱 임팩트",
    "Climate Home News": "🌱 임팩트",
    "Inside Climate News": "🌱 임팩트",
    "Bloomberg Green": "🌱 임팩트",
    "CleanTechnica": "🌱 임팩트",
    "Energy Voice": "🌱 임팩트",

    # 👔 MBB·Big4 인사이트
    "McKinsey Insights": "👔 MBB·Big4 인사이트",
    "BCG Insights": "👔 MBB·Big4 인사이트",
    "PwC strategy+business": "👔 MBB·Big4 인사이트",

    # 🤖 AI
    "The Batch": "🤖 AI",
    "The Batch (deeplearning.ai)": "🤖 AI",
    "SemiAnalysis": "🤖 AI",
    "VentureBeat AI": "🤖 AI",
    "MIT Tech Review (AI)": "🤖 AI",

    # 💼 대체투자
    "Crunchbase News": "💼 대체투자",
    "TechCrunch Venture": "💼 대체투자",
    "PE Hub": "💼 대체투자",
    "Sifted": "💼 대체투자",
}
