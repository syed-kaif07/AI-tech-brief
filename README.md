# Tech Brief — Daily AI/Tech Email Brief

Fetches last 24h of curated tech + AI/LLM RSS feeds, filters + ranks by relevance, formats into a clean HTML email, and sends it to your Gmail. Runs automatically every day at 7 AM IST via GitHub Actions.



## ⚡ Quick Start

1. Clone
   ```bash
   git clone <your-repo-url>
   cd "AI TECH BRIEF GMAIL SETUP"
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Add your secrets to `.env`
   ```env
   RESEND_API_KEY=re_...
   SENDER_EMAIL=AI Brief <onboarding@resend.dev>
   RECIPIENT_EMAIL=you@gmail.com
   ```

4. Test once
   ```bash
   python fetch_and_send.py
   ```
   Check your inbox. If it works, run it once manually whenever you want a fresh brief.

## 🔁 Automation (GitHub Actions)

The cron in `.github/workflows/daily-brief.yml` runs:

- **7 AM IST** every day (default)
- Optional second run: uncomment/add a second `cron` in the same file

### Changing the schedule
Edit `.github/workflows/daily-brief.yml`:

```yaml
on:
  schedule:
    - cron: '0 1:30 * * *'   # 7:00 AM IST
    - cron: '0 8:30 * * *'   # 2:00 PM IST (uncomment for second daily run)
  workflow_dispatch:         # allows manual "Run workflow" from GitHub UI
```

GitHub cron uses **UTC**. IST = UTC + 5:30.

## 📰 Feeds

Edit `feeds.json`. Current sources (as of build):

- TechCrunch AI
- The Verge
- Ars Technica
- Anthropic Blog
- OpenAI Blog
- MIT Technology Review
- r/MachineLearning (Reddit RSS)
- r/hardware (Reddit RSS)
- r/AI_Agents (Reddit RSS)

To add a feed:
```json
{ "name": "Source Name", "url": "https://example.com/rss", "category": "ai" }
```

## 📄 Output

- `public/data/daily-brief.json` — machine-readable result written after every successful run
- HTML email — sent via Resend

## 🛠 Tech Stack

- Python 3.11+
- feedparser — RSS fetching
- resend — email delivery
- GitHub Actions — scheduler
- dotenv — local secrets

## 🔒 Secrets

Never commit real API keys. `.env` is gitignored. In GitHub, set secrets under **Settings → Secrets and variables → Actions**:

- `RESEND_API_KEY`
- `RECIPIENT_EMAIL`
- `SENDER_EMAIL`

If running locally only, `.env` is enough.

## 📦 Project Structure

```
AI TECH BRIEF GMAIL SETUP/
├── fetch_and_send.py          # main script: fetch → filter → format → send
├── feeds.json                 # RSS sources
├── requirements.txt
├── .env                       # your secrets (gitignored)
├── .github/
│   └── workflows/
│       └── daily-brief.yml    # cron + sender
└── public/
    └── data/
        └── daily-brief.json   # generated output (gitignored)
```

## ✅ Done

After setup:
- You get one email per scheduled run
- JSON archive builds up locally / in repo artifacts
- Add/remove feeds anytime in `feeds.json`

Open an issue or PR if you want changes to formatting or sources.
