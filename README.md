# 📰 Daily Tech & Startup News Bot

A free Telegram bot that fetches, deduplicates, and summarizes daily tech/startup news from multiple sources — runs entirely on GitHub Actions.

---

## ✨ Features

- 🔍 Fetches from 7 sources: Hacker News, TechCrunch, MIT Technology Review, Wired, The Verge, Product Hunt, Reddit
- 🧠 Semantic deduplication — merges the same story from multiple sources into one card
- 📝 AI-generated 4-line summaries via Gemini API
- 🏷 Auto-tagging and field/category detection
- 📱 Delivers directly to your Telegram
- 🔁 No duplicate articles across days
- 🔧 Daily error report sent to Telegram

---

## 📋 Requirements

| Tool | Purpose | Free? |
|---|---|---|
| GitHub Account | Runs the bot via Actions | ✅ |
| Telegram Bot | Delivers the news | ✅ |
| Gemini API Key | Summarization + tagging | ✅ (free tier) |

---

## 🚀 Setup

### Step 1 — Fork this repo
Click **Fork** at the top right of this page.

### Step 2 — Create a Telegram Bot
1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the steps
3. Save the **Bot Token**
4. Get your **Chat ID** from [@userinfobot](https://t.me/userinfobot)
5. Start your bot by sending `/start` to it

### Step 3 — Get a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a free API key

### Step 4 — Add GitHub Secrets
Go to your forked repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these 3 secrets:

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID from userinfobot |
| `GEMINI_API_KEY` | Your Gemini API key |

### Step 5 — Enable Actions & Test
1. Go to **Actions** tab → Enable workflows
2. Click **News Bot 📰** → **Run workflow** → **Run workflow**
3. Check your Telegram ✅

---

## ⚙️ Customization

### Change keywords/filters
Edit `config.py`:
- `INTEREST_KEYWORDS` — topics to include
- `BLACKLIST_KEYWORDS` — topics to exclude
- `CATEGORIES` — field detection rules

### Change schedule
Edit `.github/workflows/run.yml`:
```yaml
- cron: "30 3 * * *"  # currently 7:00 AM Tehran time
```

### Change number of articles
Edit `MAX_ARTICLES_PER_RUN` in `config.py` (default: 15).

---

## 📤 Output Format

Each article card looks like:

```
📌 Title

🗂 Field: AI & ML
🏷 Tags: startup, AI, automation
📅 Date: 2026-06-04

📝 Summary:
...4-line summary...

🔗 Sources: TechCrunch | Wired
```

---

## 🔧 Error Handling

| Scenario | Behavior |
|---|---|
| Source fetch fails | Skipped, others continue |
| Missing title/link | Article skipped |
| Missing date | Shows "Unknown date" |
| Semantic dedup fails | Falls back to title-based dedup |
| Gemini fails | Retries once, then sends without summary |
| Telegram send fails | Retries once, then logs and skips |

A daily error report is sent to your Telegram at the end of each run.
