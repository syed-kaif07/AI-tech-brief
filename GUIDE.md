# Daily AI Tech Brief — Complete Guide

Everything you need to know about this project: what it does, how it works, and how to maintain it.

---

## What This Project Does

1. Fetches tech + AI/LLM news from RSS feeds
2. Filters articles from the last 24 hours
3. Removes duplicate stories
4. Ranks them by AI relevance
5. Formats a clean dark-mode HTML email
6. Sends it to your inbox automatically every day at 7 AM IST

---

## Key Terms

### Cron / GitHub Actions
- **Cron** = scheduled task that runs automatically at set times
- **GitHub Actions** = GitHub's built-in automation tool
- **Schedule** = `0 1:30 * * *` UTC → **7:00 AM IST** (IST = UTC + 5:30)

### RSS / Atom Feeds
- **RSS** = "Really Simple Syndication" — a standard format for publishing frequently updated content (blogs, news sites, podcasts)
- **Atom** = similar to RSS, another web feed format
- The script reads these feeds and extracts article titles, links, and descriptions

### Feed Sources
The current feeds (`feeds.json`):
- **TechCrunch AI** — AI startup and product news
- **The Verge** — tech industry coverage
- **Ars Technica** — deep tech and science
- **Anthropic Blog** — Claude AI updates
- **OpenAI Blog** — GPT and research updates
- **MIT Technology Review** — AI trends and analysis
- **r/MachineLearning** (Reddit RSS) — community ML discussions
- **r/hardware** (Reddit RSS) — hardware/AI chip news
- **r/AI_Agents** (Reddit RSS) — agentic AI developments

### Deduplication
- If the same article appears in multiple feeds (e.g., TechCrunch and Reddit both link to the same story), it's counted **once** based on matching title keywords

### Relevance Scoring
- Each article gets a score based on how many AI/LLM keywords it contains
- Only articles above a certain threshold make it into the final email

---

## System Flow (Step by Step)

```
┌─────────────────────────────────────────────────────┐
│ 1. TRIGGER: GitHub Actions Cron                      │
│    Runs at 0 1:30 UTC = 7:00 AM IST daily          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ 2. SCRIPT: fetch_and_send.py starts                │
│    - Loads secrets from .env                        │
│    - Reads feed URLs from feeds.json                │
└───────┬─────────────────────────────┬───────────────┘
        │                             │
        ▼                             ▼
┌──────────────────┐      ┌──────────────────────┐
│ RSS FEEDS        │      │ SECRETS (.env)       │
│ - 9 sources     │      │ EMAIL_ADDRESS        │
│ - Fetched via   │      │ EMAIL_APP_PASSWORD   │
│   feedparser lib │      │ RECIPIENT_EMAIL      │
└────────┬─────────┘      │ SENDER_EMAIL         │
         │                └──────────────────────┘
         └──────────────┬──────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│ 3. PARSE & FILTER                                   │
│    - Extract titles, links, dates from each feed   │
│    - Keep only articles from last 24 hours          │
│    - Deduplicate by title similarity                │
│    - Score by AI keyword relevance                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ 4. FORMAT BRIEF                                     │
│    - Build dark-mode HTML email                     │
│    - Organize into 4 sections:                     │
│      1. Top Story — most important headline         │
│      2. LLM Leaderboard — rankings + pricing        │
│      3. Enterprise Agents — new tool launches       │
│      4. TL;DR for Devs — 6 key takeaways           │
└────────────────────┬────────────────────────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
    ┌─────────────────┐  ┌──────────────────┐
    │ SIDE OUTPUT     │  │ EMAIL SEND       │
    │ JSON saved to   │  │ Via Gmail SMTP   │
    │ public/data/    │  │ TLS on port 587  │
    │ daily-brief.json│  │                  │
    └─────────────────┘  └────────┬─────────┘
                                   │
                                   ▼
                    ┌────────────────────────┐
                    │ RECIPIENTS             │
                    │ syedkaifuddin4@gmail   │
                    │ rahmnatwork@gmail      │
                    └────────────────────────┘
```

---

## File Structure

```
AI-tech-brief/
├── fetch_and_send.py        # Main script — the entire pipeline
├── feeds.json               # RSS feed URLs and categories
├── requirements.txt         # Python dependencies
├── .env                     # Your secrets (NEVER commit this)
├── .env.example             # Template showing required variables
├── .gitignore               # Files Git should skip
├── README.md                # Short overview for GitHub
├── .github/workflows/       # GitHub Actions settings
│   └── daily-brief.yml      # Cron schedule + run config
├── public/
│   └── data/
│       └── daily-brief.json # Generated output (gitignored)
└── Flowchart.png            # System diagram
```

---

## Configuration Variables (`.env`)

| Variable | Purpose | Example |
|----------|---------|---------|
| `EMAIL_ADDRESS` | Your Gmail address (sender) | `syedkaifuddin777@gmail.com` |
| `EMAIL_APP_PASSWORD` | 16-char Gmail App Password | `nacb vosm huwv pufg` |
| `RECIPIENT_EMAIL` | Comma-separated recipients | `syedkaifuddin4@gmail.com,rahmnatwork@gmail.com` |
| `SENDER_EMAIL` | Display name/email for sent mail | `syedkaifuddin777@gmail.com` |
| `FEEDS_FILE` | Path to feeds config | `feeds.json` |

---

## How to Add/Remove Feeds

Edit `feeds.json`. Each entry needs:
- `name` — human-readable label
- `url` — RSS/Atom feed URL
- `category` — for filtering (e.g. `ai`, `tech`)

```json
{
  "name": "Source Name",
  "url": "https://example.com/rss",
  "category": "ai"
}
```

---

## How to Change the Schedule

Edit `.github/workflows/daily-brief.yml`:

```yaml
on:
  schedule:
    - cron: '0 1:30 * * *'   # 7:00 AM IST
    - cron: '0 8:30 * * *'   # 2:00 PM IST (optional second run)
```

**Cron format:** `minute hour day month weekday`  
**Zone:** GitHub cron uses **UTC**. IST = UTC + 5:30.

Examples:
- `0 1:30 * * *` — 7:00 AM IST
- `0 11:30 * * *` — 5:00 PM IST
- `0 3:30 * * 1-5` — 9:00 AM IST, Mon–Fri only

---

## How to Test Manually

```bash
cd "G:\AI TECH BRIEF GMAIL SETUP"
python3 fetch_and_send.py
```

Expected output:
```
[*] Fetching feeds...
[*] 15 articles found
[*] Building brief...
[*] Sending...
[OK] Sent to 2 recipient(s)
```

If you see `[ERROR]`, check the error message:
- **535 BadCredentials** → App password is wrong or 2FA is off
- **API key is invalid** → Wrong Resend key (if using Resend instead of Gmail)
- **Connection refused** → Network/SMTP blocked

---

## GitHub Secrets (for GitHub Actions)

When you push to GitHub, the workflow needs secrets stored in the repo:

**Path:** Repo → Settings → Secrets and variables → Actions → New repository secret

Required secrets:
- `EMAIL_ADDRESS`
- `EMAIL_APP_PASSWORD`
- `RECIPIENT_EMAIL`
- `SENDER_EMAIL`

GitHub Actions injects these at runtime. They never appear in logs.

---

## Troubleshooting

### Email not sending
1. Check App Password is correct (16 chars, no spaces or with spaces — script auto-strips spaces)
2. Confirm 2FA is ON for the sender Gmail account
3. Verify `RECIPIENT_EMAIL` has no typos
4. Run manually first: `python3 fetch_and_send.py`

### GitHub Actions not running
1. Check Actions tab for error logs
2. Confirm secrets are set in GitHub repo settings
3. Workflow file must be at `.github/workflows/daily-brief.yml`
4. Cron uses UTC — double-check time conversion

### No articles in email
1. Check `feeds.json` URLs are valid and reachable
2. Increase time window (currently 24h) in `fetch_and_send.py`
3. Lower relevance score threshold in the script

### Duplicate articles
- Deduplication is by **title similarity**
- If two articles have different headlines but same story, they may both appear
- Adjust the similarity threshold in the script if needed

---

## Tech Stack Summary

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| RSS parsing | `feedparser` |
| Email delivery | `smtplib` (Gmail SMTP) |
| Secrets | `python-dotenv` |
| Scheduler | GitHub Actions |
| Output | HTML email + JSON |

---

## Future Ideas

- [ ] Add a web dashboard to browse past briefs
- [ ] Add a second daily run time
- [ ] Add WhatsApp delivery channel
- [ ] Add article summaries using LLM
- [ ] Track open rates / engagement
- [ ] Add user preference filters (e.g., only hardware news)

---

## Quick Reference

**GitHub repo:** `https://github.com/syed-kaif07/AI-tech-brief`

**Local path:** `G:\AI TECH BRIEF GMAIL SETUP`

**Test command:** `python3 fetch_and_send.py`

**Schedule:** 7:00 AM IST daily (GitHub Actions cron)

**Recipients:** `syedkaifuddin4@gmail.com`, `rahmnatwork@gmail.com`

**Sender:** `syedkaifuddin777@gmail.com`
