import os

# ---------------------------------------------------------------------------
# 🤖 제미나이 모델명 빈칸 자동 방어 로직
# ---------------------------------------------------------------------------
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
if not GEMINI_MODEL or GEMINI_MODEL.strip() == "":
    os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"
    GEMINI_MODEL = "gemini-1.5-flash"

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
    "미중갈등", "중동", "우크라이나", "대만", "통화정책", "금리", "파월", "이창용", "거시경제"
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
# 4. RSS 피드 (🚀 404·접속불가 매체 제거 + 검증된 15개 글로벌 피드 & 국내 VC 매체)
# ---------------------------------------------------------------------------
LEGACY_ALL_FEEDS = {
    # [Table Verified] Venture Capital & Private Equity & Startups
    "TechCrunch Venture": "https://techcrunch.com/category/venture/feed/",
    "PE Hub": "https://www.pehub.com/feed/",
    "Sifted": "https://sifted.eu/feed",
    "Crunchbase News": "https://news.crunchbase.com/feed/",
    
    # [Table Verified] AI, Semiconductors, Cloud & Enterprise
    "MIT Tech Review (AI)": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "The Batch": "https://www.deeplearning.ai/the-batch/tag/issue/rss/",
    "EE Times": "https://www.eetimes.com/feed/",
    "Data Center Dynamics": "https://www.datacenterdynamics.com/en/rss/",
    "InfoWorld Cloud": "https://www.infoworld.com/category/cloud-computing/index.rss",
    "ZDNET Enterprise": "https://www.zdnet.com/topic/enterprise-software/rss.xml",
    "SemiAnalysis": "https://www.semianalysis.com/feed",

    # [Table Verified] Impact Investing, Climate Tech, ESG & Energy
    "Impact Alpha": "https://impactalpha.com/feed/",
    "ESG Today": "https://www.esgtoday.com/feed/",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "Energy Voice": "https://www.energyvoice.com/feed/",

    # [Table Verified] Macroeconomics, Geopolitics & Consulting
    "The Economist": "https://www.economist.com/finance-and-economics/rss.xml",
    "Foreign Affairs": "https://www.foreignaffairs.com/rss.xml",
    "BCG Insights": "https://www.bcg.com/rss",
    "McKinsey Insights": "https://www.mckinsey.com/insights/rss",
    "PwC strategy+business": "https://www.strategy-business.com/rss",

    # [Korea Top] 국내 VC 및 임팩트 생태계 매체
    "ImpactOn (임팩트온)": "https://www.impacton.net/rss/allArticle.xml",
    "Platum (플랫텀)": "https://platum.kr/feed",
    "VentureSquare (벤처스퀘어)": "https://www.venturesquare.net/feed",
    "한경 Geeks": "https://rss.hankyung.com/feed/geeks.xml",
    "전자신문 스타트업": "https://rss.etnews.com/Section902.xml",
}
# RSS is configured by editorial category and priority tier. The fetcher keeps
# consuming ALL_FEEDS for backward compatibility, while its insertion order
# ensures overseas primary sources are checked before domestic supplements.
CATEGORY_RSS_SOURCES = {
    "🌱 임팩트": {
        "primary": {
            "Impact Alpha": "https://impactalpha.com/feed/",
            "NextBillion": "https://nextbillion.net/feed/",
            "Stanford Social Innovation Review": "https://ssir.org/site/rss_2.0/",
            "Pioneers Post": "https://www.pioneerspost.com/rss.xml",
            "Carbon Brief": "https://www.carbonbrief.org/feed/",
            "Responsible Investor": "https://www.responsible-investor.com/feed/",
        },
        "supplemental": {
            "ImpactOn": "https://www.impacton.net/rss/allArticle.xml",
        },
    },
    "🤖 AI": {
        "primary": {
            "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "SemiAnalysis": "https://www.semianalysis.com/feed",
            "MIT Tech Review (AI)": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        },
        "supplemental": {},
    },
    "💼 대체투자": {
        "primary": {
            "PE Hub": "https://www.pehub.com/feed/",
            "Crunchbase News": "https://news.crunchbase.com/feed/",
            "Sifted": "https://sifted.eu/feed",
            "TechCrunch Venture": "https://techcrunch.com/category/venture/feed/",
        },
        "supplemental": {},
    },
    "🌐 거시경제·정책·지정학": {
        "primary": {
            "The Economist": "https://www.economist.com/finance-and-economics/rss.xml",
            "Foreign Affairs": "https://www.foreignaffairs.com/rss.xml",
        },
        "supplemental": {},
    },
    "👔 MBB·Big4 인사이트": {
        "primary": {
            "McKinsey Insights": "https://www.mckinsey.com/insights/rss",
        },
        "supplemental": {},
    },
}

RSS_SOURCE_METADATA = {
    source_name: {"category": category, "tier": tier}
    for category, tiers in CATEGORY_RSS_SOURCES.items()
    for tier, sources in tiers.items()
    for source_name in sources
}
ALL_FEEDS = {
    source_name: feed_url
    for tiers in CATEGORY_RSS_SOURCES.values()
    for sources in tiers.values()
    for source_name, feed_url in sources.items()
}
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
