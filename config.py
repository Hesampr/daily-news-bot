# 1. 수집하고 싶은 핵심 관심 키워드 (4대 주제별 영문+한글 키워드)
INTEREST_KEYWORDS = [
    # 🌱 임팩트 (ESG, 기후테크, 친환경, 돌봄, 시니어, 임팩트 투자)
    "esg", "climate tech", "social impact", "clean energy", "sustainability",
    "renewable", "circular economy", "green tech", "carbon", "emission",
    "energy transition", "elderly care", "senior care", "impact investing",
    "소셜임팩트", "기후테크", "친환경", "탄소중립", "순환경제", "신재생에너지",
    "돌봄", "시니어", "임팩트투자", "사회적가치",
    
    # 🤖 AI (생성형 AI, LLM, 머신러닝, 인공지능 산업)
    "artificial intelligence", "machine learning", "generative ai", "llm",
    "gpt", "openai", "anthropic", "gemini", "neural network", "deep learning",
    "ai model", "agentic ai",
    "생성형 ai", "인공지능", "거대언어모델", "머신러닝", "딥러닝",
    
    # 💼 대체투자 (PE, VC, AC, 스타트업 투자, M&A)
    "venture capital", "private equity", "seed round", "series a", "series b",
    "mergers and acquisitions", "m&a", "startup funding", "accelerator",
    "fundraising", "valuation", "vc fund", "pe fund", "buyout",
    "스타트업", "벤처캐피탈", "액셀러레이터", "모태펀드", "사모펀드",
    "시드", "시리즈a", "시리즈b", "투자유치", "인수합병", "펀드결성", "밸류에이션",
    
    # 🌐 거시경제 (금리, 인플레이션, 미 연준, 한국은행, 경기 동향)
    "interest rate", "inflation", "federal reserve", "fed", "central bank",
    "monetary policy", "gdp", "recession", "economic growth", "macroeconomy",
    "tariff", "bond yield",
    "거시경제", "금리", "인플레이션", "한국은행", "기준금리", "경기침체",
    "통화정책", "환율"
]

# 2. 기존 분류 체계 (AI 분류 실패 시 키워드 기반으로 분류하는 보조 장치)
CATEGORIES = {
    "🌱 임팩트": [
        "esg", "climate", "sustainability", "green tech", "renewable",
        "carbon", "clean energy", "social impact", "circular economy",
        "소셜임팩트", "기후테크", "친환경", "탄소중립", "순환경제", "임팩트투자"
    ],
    "🤖 AI": [
        "artificial intelligence", "machine learning", "deep learning",
        "llm", "gpt", "neural", "ai model", "generative",
        "생성형 ai", "인공지능", "거대언어모델", "머신러닝", "딥러닝"
    ],
    "💼 대체투자": [
        "venture capital", "private equity", "funding", "seed round",
        "series a", "series b", "m&a", "accelerator", "buyout",
        "스타트업", "벤처캐피탈", "액셀러레이터", "모태펀드", "사모펀드", "투자유치", "인수합병"
    ],
    "🌐 거시경제": [
        "interest rate", "inflation", "federal reserve", "fed",
        "central bank", "gdp", "recession", "macroeconomy",
        "거시경제", "금리", "인플레이션", "한국은행", "기준금리", "환율"
    ],
    "🌐 거시경제": []  # fallback 기본값
}

# 3. 절대 수집하면 안 되는 블랙리스트 (광고, 쿠폰, 쇼핑, 제품 리뷰, 정치/연예 차단)
BLACKLIST_KEYWORDS = [
    # 스팸 / 쇼핑 / 프로모션 차단
    "coupon", "promo", "discount", "off", "deal", "airdoctor", "booking.com",
    "laptop", "review", "best laptop", "best price", "sale", "buy now",
    
    # 연예 / 스포츠 / 일반 정치 차단
    "celebrity", "sports", "entertainment", "gaming", "politics",
    "election", "movie", "tv show", "gossip"
]

# 4. 뉴스 수집 사이트 (RSS 피드) - 국내외 핵심 매체 통합
RSS_SOURCES = {
    # --- 🇰🇷 국내 스타트업 / VC / ESG / IT 비즈니스 ---
    "Platum (플랫텀)": "https://platum.kr/feed",
    "VentureSquare (벤처스퀘어)": "https://www.venturesquare.net/feed",
    "ImpactOn (임팩트온)": "http://www.impacton.net/rss/allArticle.xml",
    "한경 Geeks (벤처/VC)": "https://rss.hankyung.com/feed/geeks.xml",
    "전자신문 (벤처/스타트업)": "https://rss.etnews.com/Section902.xml",
    
    # --- 🌍 해외 🌱 임팩트 & 👔 MBB 비즈니스 전략 ---
    "ImpactAlpha": "https://impactalpha.com/feed/",
    "ESG Today": "https://www.esgtoday.com/feed/",
    "McKinsey Insights": "https://www.mckinsey.com/insights/rss",
    "Strategy+Business (PwC)": "https://www.strategy-business.com/rss",
    "MIT Sloan Management": "https://sloanreview.mit.edu/feed/",
    
    # --- 🚀 해외 글로벌 테크 & 대체투자 ---
    "TechCrunch": "https://techcrunch.com/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "Wired": "https://www.wired.com/feed/rss",
}
# 5. Hacker News 검색어 (4대 주제별 대표 검색어)
HN_KEYWORDS = [
    "climate tech", "ESG", "AI", "llm", "venture capital",
    "private equity", "inflation", "federal reserve"
]

# 6. 설정 옵션
SIMILARITY_THRESHOLD = 0.75
MAX_ARTICLES_PER_RUN = 15
