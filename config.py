import os

# ---------------------------------------------------------------------------
# 🤖 [추가] 제미나이 모델명 빈칸 방어 로직 (Variables 수정 안 해도 됨!)
# ---------------------------------------------------------------------------
# 깃허브 변수가 비어있거나 없으면 무조건 'gemini-1.5-flash'를 기본으로 사용
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
if not GEMINI_MODEL or GEMINI_MODEL.strip() == "":
    os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"
    GEMINI_MODEL = "gemini-1.5-flash"

# ---------------------------------------------------------------------------
# 1. 관심 키워드 (이 단어가 있어야 수집됨)
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
# 2. 카테고리 정의
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
LLM_SEND_MIN_SCORE = 0  # 0으로 두어 LLM 편집장이 자율적으로 고르도록 함

# ---------------------------------------------------------------------------
# 3. 블랙리스트 (노이즈 철저 차단!)
# ---------------------------------------------------------------------------
BLACKLIST_KEYWORDS = [
    "coupon", "promo code", "discount code", "% off", "best deals",
    "best price", "buy now", "airdoctor", "booking.com", "best laptop",
    "laptop review", "celebrity", "sports", "entertainment", "gaming",
    "movie", "tv show", "gossip", "github repo", "code walkthrough",
    "배임", "횡령", "파업",
    # 지자체·소상공인 노이즈 차단
    "중기자금", "소상공인", "지역화폐", "테크노파크", "지자체",
    "인천시", "서울시", "경기도", "부산시", "대구시", "광주시", "대전시", "울산시",
    "경남도", "경북도", "전남도", "전북도", "충남도", "충북도", "강원도", "제주도",
    "특례보증", "육성자금", "이차보전", "도청", "시청"
]

# ---------------------------------------------------------------------------
# 4. RSS 피드 (🚀 띄어쓰기 오류 100% 해결 완료!)
# ---------------------------------------------------------------------------
RSS_FEEDS = {
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

# 🚀 구글 뉴스 주소 내 띄어쓰기(공백)를 안전한 URL 인코딩(%20, +)으로 완벽 변환
GOOGLE_NEWS_FEEDS = {
    "국내 투자유치": "https://news.google.com/rss/search?q=(%EC%8B%9C%EB%A6%AC%EC%A6%88A+%EC%8B%9C%EB%A6%AC%EC%A6%88B+%ED%94%84%EB%A6%ACIPO)+%ED%88%AC%EC%9E%90%EC%9C%A0%EC%B9%98&hl=ko&gl=KR&ceid=KR:ko",
    "펀드결성/출자": "https://news.google.com/rss/search?q=(%EB%B2%A4%EC%B2%98%ED%8E%80%EB%93%9C+%EB%AA%A8%ED%83%9C%ED%8E%80%EB%93%9C)+(%EA%B2%B0%EC%84%B1+%EC%B6%9C%EC%9E%90%EC%82%AC%EC%97%85)&hl=ko&gl=KR&ceid=KR:ko",
    "M&A/회수": "https://news.google.com/rss/search?q=%EC%8A%A4%ED%83%80%ED%8A%B8%EC%97%85+(%EC%9D%B8%EC%88%98+M%26A+%EC%83%81%EC%9E%A5)&hl=ko&gl=KR&ceid=KR:ko",
    "글로벌 VC 라운드": "https://news.google.com/rss/search?q=startup+(Series+funding+round+raises)&hl=ko&gl=KR&ceid=KR:ko",
    "AI 투자/펀딩": "https://news.google.com/rss/search?q=AI+%EC%8A%A4%ED%83%80%ED%8A%B8%EC%97%85+(%ED%88%AC%EC%9E%90%EC%9C%A0%EC%B9%98+%ED%8E%80%EB%94%A9)&hl=ko&gl=KR&ceid=KR:ko",
    "AI 반도체/인프라": "https://news.google.com/rss/search?q=(AI+%EB%B0%98%EB%8F%84%EC%B2%B4+GPU+%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%84%BC%ED%84%B0)+(%EC%97%94%EB%B9%84%EB%94%94%EC%95%84+%ED%88%AC%EC%9E%90)&hl=ko&gl=KR&ceid=KR:ko",
    "생성형 AI 동향": "https://news.google.com/rss/search?q=(%EC%83%9D%EC%84%B1%ED%98%95+AI+LLM+%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8)&hl=ko&gl=KR&ceid=KR:ko",
    "미국 통화정책": "https://news.google.com/rss/search?q=FOMC+%EC%97%B0%EC%A4%80+%ED%8C%8C%EC%9B%94+%EA%B8%88%EB%A6%AC&hl=ko&gl=KR&ceid=KR:ko",
    "트럼프 관세/세제": "https://news.google.com/rss/search?q=%ED%8A%B8%EB%9F%BC%ED%94%84+(%EA%B4%80%EC%84%B8+%EC%83%81%ED%98%B8%EA%B4%80%EC%84%B8+%EA%B0%90%EC%84%B8)&hl=ko&gl=KR&ceid=KR:ko",
    "IRA·반도체 정책": "https://news.google.com/rss/search?q=(IRA+%EC%B9%A9%EC%8A%A4%EB%B2%95)+(%EB%B0%B0%ED%84%B0%EB%A6%AC+%EB%B0%98%EB%8F%84%EC%B2%B4+%EB%B3%B4%EC%A1%B0%EA%B8%88)&hl=ko&gl=KR&ceid=KR:ko",
    "한은 통화정책": "https://news.google.com/rss/search?q=%ED%95%9C%EA%B5%AD%EC%9D%80%ED%96%89+(%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC+%ED%99%98%EC%9C%A8)&hl=ko&gl=KR&ceid=KR:ko",
    "임팩트/기후정책": "https://news.google.com/rss/search?q=%EA%B8%B0%ED%9B%84%EB%B6%80+%EC%9E%AC%EC%83%9D%EC%97%90%EB%84%88%EC%A7%80+%EB%85%B9%EC%83%89%EC%B1%84%EA%B6%8C&hl=ko&gl=KR&ceid=KR:ko",
    "Global impact/climate": "https://news.google.com/rss/search?q=(impact+investing+climate+tech)+funding&hl=en-US&gl=US&ceid=US:en",
    "Global AI funding": "https://news.google.com/rss/search?q=AI+startup+(raises+funding+round+valuation)&hl=en-US&gl=US&ceid=US:en",
    "Global VC/PE deals": "https://news.google.com/rss/search?q=(venture+capital+private+equity)+(fund+round+acquisition)&hl=en-US&gl=US&ceid=US:en",
    "MBB/Big4 insights": "https://news.google.com/rss/search?q=(McKinsey+BCG+Bain+Deloitte)+(AI+climate+private+equity)&hl=en-US&gl=US&ceid=US:en"
}
