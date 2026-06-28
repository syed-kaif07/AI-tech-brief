# Daily AI Tech Brief

Automated daily email with the latest AI/LLM and tech news. Fetches RSS feeds from the last 24 hours, filters for relevance, formats a clean dark-mode HTML brief, and sends it to your inbox.

**Schedule:** 7:00 AM IST daily  
**Delivery:** Gmail SMTP  
**Recipients:** Configured via `.env`

---

## System Flow

![Daily AI Tech Brief — System Flow](https://raw.githubusercontent.com/syed-kaif07/AI-tech-brief/main/Flowchart.png)

---

## Quick Start

```bash
git clone https://github.com/syed-kaif07/AI-tech-brief.git
cd "AI-tech-brief"
pip install -r requirements.txt
```

Add secrets to `.env` (copy from `.env.example`):

```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_APP_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient1@email.com,recipient2@email.com
SENDER_EMAIL=your-email@gmail.com
```

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
