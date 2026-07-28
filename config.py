# 1. 수집하고 싶은 핵심 관심 키워드 (4대 주제별 영문+한글 키워드)
INTEREST_KEYWORDS = [
    # 🌱 임팩트 (ESG, 기후테크, 친환경, 돌봄, 시니어, 임팩트 투자)
    "기후리스크", "기후테크", "돌봄", "사회적가치", "소셜임팩트",
    "순환경제", "시니어", "신재생에너지", "에너지전환", "ESG 공시",
    "임팩트투자", "탄소국경세", "탄소중립", "친환경", "CBAM",
    "carbon", "carbon border", "cbam", "circular economy", "clean energy",
    "climate risk", "climate tech", "elderly care", "emission", "energy transition",
    "esg", "esg disclosure", "green tech", "impact investing", "renewable",
    "renewable energy", "senior care", "social impact", "sustainability",
    
    # 🤖 AI (생성형 AI, LLM, 머신러닝, 인공지능 산업)
    "거대언어모델", "머신러닝", "딥러닝", "반도체", "설비투자",
    "생성형 ai", "수출규제", "인공지능", "엔비디아", "자본지출",
    "파운드리", "ai 버블",
    "agentic ai", "ai capex", "ai infrastructure", "ai model", "ai valuation",
    "anthropic", "artificial intelligence", "deep learning", "export control", "foundry",
    "gemini", "generative ai", "generative ai business", "gpt", "hbm",
    "llm", "machine learning", "neural network", "nvidia", "openai", "semiconductor",
    
    # 💼 대체투자 (PE, VC, AC, 스타트업 투자, M&A)
    "기업공개", "모태펀드", "밸류에이션", "벤처캐피탈", "사모펀드",
    "스타트업", "시드", "시리즈a", "시리즈b", "액셀러레이터",
    "인수합병", "투자유치", "펀드결성",
    "accelerator", "buyout", "fundraising", "ipo", "m&a",
    "mergers and acquisitions", "pe fund", "private equity", "seed round", "series a",
    "series b", "startup funding", "valuation", "vc fund", "venture capital",
    
    # 🌐 거시경제 (금리, 인플레이션, 미 연준, 한국은행, 경기 동향)
    "거시경제", "경기침체", "관세", "국채금리", "금리",
    "기준금리", "무역갈등", "소비자물가", "유동성", "인플레이션",
    "점도표", "통화정책", "한국은행", "환율",
    "bond yield", "central bank", "cpi", "economic growth", "exchange rate",
    "fed", "federal reserve", "fomc", "gdp", "inflation",
    "interest rate", "krw", "liquidity", "macroeconomy", "monetary policy",
    "ppi", "protectionism", "recession", "tariff", "trade war", "usd"
]

# 2. 키워드 기반 카테고리 자동 분류 체계
CATEGORIES = {
    "🌱 임팩트": [
        "esg", "climate", "sustainability", "green tech", "renewable",
        "carbon", "clean energy", "social impact", "circular economy", "cbam",
        "기후리스크", "소셜임팩트", "기후테크", "친환경", "탄소중립", "순환경제", "임팩트투자", "esg 공시"
    ],
    "🤖 AI": [
        "artificial intelligence", "machine learning", "deep learning",
        "llm", "gpt", "ai model", "generative", "nvidia", "semiconductor", "hbm", "foundry", "ai capex",
        "생성형 ai", "인공지능", "거대언어모델", "머신러닝", "딥러닝", "엔비디아", "반도체", "파운드리", "수출규제"
    ],
    "💼 대체투자": [
        "venture capital", "private equity", "funding", "seed round",
        "series a", "series b", "m&a", "accelerator", "buyout", "ipo", "valuation",
        "스타트업", "벤처캐피탈", "액셀러레이터", "모태펀드", "사모펀드", "투자유치", "인수합병", "기업공개", "밸류에이션"
    ],
    "🌐 거시경제": [
        "interest rate", "inflation", "federal reserve", "fed", "central bank",
        "gdp", "recession", "macroeconomy", "fomc", "cpi", "tariff", "trade war", "exchange rate",
        "거시경제", "금리", "인플레이션", "한국은행", "기준금리", "환율", "관세", "무역갈등", "소비자물가", "국채금리"
    ]
}

# 3. 절대 수집하면 안 되는 블랙리스트 (광고, 쿠폰, 쇼핑, 개발자 벤치마크 차단)
BLACKLIST_KEYWORDS = [
    # 스팸 / 쇼핑 / 프로모션 차단
    "coupon", "promo", "discount", "off", "deal", "airdoctor", "booking.com",
    "laptop", "review", "best laptop", "best price", "sale", "buy now",
    
    # 연예 / 스포츠 / 일반 정치 차단
    "celebrity", "sports", "entertainment", "gaming", "politics",
    "election", "movie", "tv show", "gossip",
    
    # 개발자 튜토리얼 / 단순 코드 리뷰 차단
    "github repo", "code walkthrough", "benchmarking"
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

# 5. Hacker News 검색어 (개발자용 슬롭을 줄이고 투자/산업에 집중)
HN_KEYWORDS = [
    "climate tech", "ESG", "Nvidia", "AI funding", "AI capex",
    "venture capital", "private equity", "inflation", "federal reserve"
]

# 6. 설정 옵션
SIMILARITY_THRESHOLD = 0.75
MAX_ARTICLES_PER_RUN = 15
