# Daily AI Tech Brief

Automated daily email with the latest AI/LLM and tech news. Fetches RSS feeds from the last 24 hours, filters for relevance, formats a clean dark-mode HTML brief, and sends it to your inbox.

**Schedule:** 7:00 AM IST daily  
**Delivery:** Gmail SMTP  
**Recipients:** syedkaifuddin4@gmail.com, rahmnatwork@gmail.com

---

## System Flow

View the system diagram: open `flowchart.html` in your browser.

---

## Quick Start

```bash
git clone https://github.com/syed-kaif07/AI-tech-brief.git
cd "AI-tech-brief"
pip install -r requirements.txt
```

Add secrets to `.env`:

```env
EMAIL_ADDRESS=syedkaifuddin777@gmail.com
EMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=syedkaifuddin4@gmail.com,rahmnatwork@gmail.com
SENDER_EMAIL=syedkaifuddin777@gmail.com
```

Test once:

```bash
python3 fetch_and_send.py
```

---

## Automation

GitHub Actions cron is at `.github/workflows/daily-brief.yml`.

| Schedule | Cron (UTC) | IST |
|----------|-----------|-----|
| Daily 7 AM | `0 1:30 * * *` | 7:00 AM IST |

Add a second run by adding another `cron` line in the workflow file.

---

## Feeds

Edit `feeds.json` to add/remove sources.

**Current sources:** TechCrunch AI, The Verge, Ars Technica, Anthropic Blog, OpenAI Blog, MIT Technology Review, r/MachineLearning, r/hardware, r/AI_Agents.

---

## Output

- **Email:** HTML brief sent to all recipients
- **JSON:** `public/data/daily-brief.json` (machine-readable archive)

---

## Tech Stack

- Python + `feedparser`
- Gmail SMTP (TLS)
- GitHub Actions

---

## Notes

- `.env` is gitignored — never commit secrets
- Run `python3 fetch_and_send.py` anytime for an instant manual brief
- For GitHub automation, add the same secrets under **Settings → Secrets and variables → Actions**
