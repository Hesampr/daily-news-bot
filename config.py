INTEREST_KEYWORDS = [
    "startup",
    "founder",
    "innovation",
    "real-world problem",
    "AI",
    "artificial intelligence",
    "machine learning",
    "fintech",
    "healthtech",
    "climate tech",
    "deep tech",
    "product launch",
    "funding",
    "venture",
    "technology solution",
    "disruption",
    "open source",
    "developer tools",
    "automation",
    "problem solving",
]

CATEGORIES = {
    "AI & ML": ["artificial intelligence", "machine learning", "deep learning", "llm", "gpt", "neural", "ai model", "generative"],
    "Fintech": ["fintech", "payment", "banking", "crypto", "blockchain", "finance", "neobank"],
    "Health Tech": ["healthtech", "medical", "healthcare", "biotech", "mental health", "digital health"],
    "Climate Tech": ["climate", "sustainability", "green tech", "renewable", "carbon", "clean energy"],
    "Startup & Entrepreneurship": ["startup", "founder", "funding", "venture", "seed round", "series a", "ipo", "accelerator"],
    "Developer Tools": ["developer", "open source", "framework", "sdk", "api", "devtools", "infrastructure"],
    "General Tech": [],  # fallback
}

BLACKLIST_KEYWORDS = [
    "celebrity",
    "sports",
    "entertainment",
    "gaming",
    "politics",
    "election",
    "movie",
    "tv show",
]

RSS_SOURCES = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "Wired": "https://www.wired.com/feed/rss",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Product Hunt": "https://www.producthunt.com/feed",
}

REDDIT_SUBREDDITS = ["startups", "technology"]

HN_KEYWORDS = ["startup", "AI", "innovation", "technology"]

SIMILARITY_THRESHOLD = 0.75

MAX_ARTICLES_PER_RUN = 15
