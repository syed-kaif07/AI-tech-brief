import os, json, datetime, re, html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "syedkaifuddin4@gmail.com")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
RECIPIENT_FILE = os.getenv("RECIPIENT_FILE", "recipients.json")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", EMAIL_ADDRESS)

FEEDS_FILE = "feeds.json"
OUTPUT_FILE = "public/data/daily-brief.json"
HOURS_LOOKBACK = int(os.getenv("HOURS_LOOKBACK", "24"))
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "25"))

KEYWORDS_WEIGHT = [
    "agent","agentic","llm","language model","gpt","claude","openai",
    "anthropic","deepseek","llama","gemini","groq","mistral","qwen",
    "multimodal","rag","fine-tun","inference","token","prompt",
    "ai chip","nvidia","blackwell","h100","h200","tpu","edge ai",
    "quantum","cybersecurity","autonomous","robot","humanoid","agi",
    "reasoning","chain-of-thought","mcp","a2a","tool use","crewai",
    "langchain","vector","embedding","fine-tuning"
]

# ─── HELPERS ───────────────────────────────────────────────────────────────

def parse_pub_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
    return None

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:220] + "..." if len(text) > 220 else text

def relevance_score(title, summary, keywords):
    text = f"{title} {summary}".lower()
    return sum(1 for kw in keywords if kw in text)

def classify_topic(title, summary):
    text = f"{title} {summary}".lower()
    if any(k in text for k in ["agent","agentic","autonomous","crewai","langchain","mcp","a2a"]): return "Agentic AI"
    if any(k in text for k in ["llm","gpt","claude","openai","anthropic","deepseek","llama","gemini","mistral"]): return "LLMs"
    if any(k in text for k in ["chip","nvidia","blackwell","h100","h200","tpu","gpu","semiconductor"]): return "AI Chips"
    if any(k in text for k in ["quantum"]): return "Quantum"
    if any(k in text for k in ["cybersecurity","security","vulnerability","breach"]): return "Cybersecurity"
    if any(k in text for k in ["robot","humanoid","embodied"]): return "Robotics"
    return "General Tech"

def deduplicate(entries, title_key="title"):
    seen = set()
    unique = []
    for e in entries:
        norm = re.sub(r'[^a-z0-9]', '', e.get(title_key, "").lower())[:60]
        if norm and norm not in seen:
            seen.add(norm)
            unique.append(e)
    return unique

# ─── FETCH ─────────────────────────────────────────────────────────────────

def fetch_feeds(feeds_path=FEEDS_FILE):
    with open(feeds_path, "r", encoding="utf-8") as f:
        feeds_config = json.load(f)["feeds"]

    entries = []
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(hours=HOURS_LOOKBACK)

    for feed_info in feeds_config:
        try:
            parsed = feedparser.parse(feed_info["url"])
            feed_title = parsed.feed.get("title", feed_info["name"])
            for entry in parsed.entries:
                pub = parse_pub_date(entry)
                if pub is None or pub < cutoff:
                    continue
                entries.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "summary": clean_text(entry.get("summary", entry.get("description", ""))),
                    "published": pub.isoformat(),
                    "source": feed_title,
                    "category": feed_info.get("category", "General"),
                })
        except Exception as e:
            print(f"[WARN] {feed_info['name']}: {e}")

    entries.sort(key=lambda x: x["published"], reverse=True)
    entries = deduplicate(entries)

    for e in entries:
        e["relevance"] = relevance_score(e["title"], e["summary"], KEYWORDS_WEIGHT)
    entries.sort(key=lambda x: (-x["relevance"], x["published"]))
    return entries[:MAX_ARTICLES]

# ─── FORMAT BRIEF ──────────────────────────────────────────────────────────

def build_brief(entries):
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%B %d, %Y")

    source_counts = {}
    for e in entries:
        source_counts[e["source"]] = source_counts.get(e["source"], 0) + 1
    total = len(entries) or 1
    breakdown = {src: round((cnt / total) * 100) for src, cnt in source_counts.items()}

    topic_counter = {}
    for e in entries:
        topic = classify_topic(e["title"], e["summary"])
        topic_counter[topic] = topic_counter.get(topic, 0) + 1
    trending = sorted(topic_counter.items(), key=lambda x: -x[1])[:5]

    articles = [{
        "title": e["title"],
        "source": e["source"],
        "timeAgo": _time_ago(e["published"]),
        "url": e["link"],
        "summary": e["summary"],
    } for e in entries]

    summary_text = (
        f"{len(entries)} relevant stories from your source feeds. "
        "Key angles: agentic AI progression, new model releases, pricing pressure, "
        "enterprise adoption, and compute supply chain shifts."
    )

    top = entries[0] if entries else None
    brief = {
        "generatedAt": now.isoformat(),
        "date": date_str,
        "summary": summary_text,
        "topStory": {
            "title": "Today's AI/Tech Brief",
            "readTime": "4 min",
            "headline": top["title"] if top else "No new stories",
            "url": top["link"] if top else "#"
        } if top else None,
        "trendingTopics": [{"name": n, "count": c} for n, c in trending],
        "newsCards": _build_news_cards(entries),
        "highlights": _build_highlights(entries, trending),
        "sourceBreakdown": breakdown,
        "articles": articles,
    }
    return brief


def _time_ago(pub_iso):
    try:
        pub = datetime.datetime.fromisoformat(pub_iso)
        delta = datetime.datetime.now(datetime.timezone.utc) - pub
        mins = int(delta.total_seconds() // 60)
        if mins < 60:
            return f"{mins}m ago"
        hrs = mins // 60
        return f"{hrs}h ago" if hrs < 24 else f"{hrs // 24}d ago"
    except Exception:
        return "recently"


def _build_news_cards(entries):
    cards = []
    desired = ["Agentic AI", "LLMs", "AI Chips", "Quantum", "Cybersecurity", "General Tech"]
    for cat in desired:
        if len(cards) >= 4:
            break
        hits = [e for e in entries if classify_topic(e["title"], e["summary"]) == cat]
        if not hits:
            continue
        top = hits[0]
        related = [e for e in entries if e["link"] != top["link"]][:2]
        bullets = [e["title"] for e in related] or ["No related stories"]
        cards.append({
            "category": cat,
            "headline": top["title"],
            "bullets": bullets,
            "url": top["link"],
        })
    return cards


def _build_highlights(entries, trending):
    if not entries:
        return []
    top = entries[0]
    topic = trending[0][0] if trending else "AI"
    return [{
        "topic": topic,
        "headline": top["title"],
        "url": top["link"],
        "whyItMatters": (
            f"Top story today centers on {topic.lower()}. "
            "Market and developer signals indicate this will affect pricing, "
            "tooling choices, and enterprise adoption in the next quarter."
        ),
    }]

# ─── EMAIL FORMAT ──────────────────────────────────────────────────────────

def build_html_email(brief):
    date_str = brief["date"]
    articles = brief.get("articles", [])
    styles = """
    <style>
      body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a0a0a;color:#e5e7eb;margin:0;padding:0}
      .container{max-width:720px;margin:0 auto;padding:24px 16px}
      .section{background:#0f0f0f;border:1px solid #1f1f1f;border-radius:12px;padding:20px 24px;margin-bottom:16px}
      .section-title{font-size:16px;font-weight:700;margin:0 0 12px;color:#fff}
      .bullet{padding:5px 0;color:#d1d5db;font-size:14px;line-height:1.6}
      .bullet:last-child{border-bottom:none}
      a{color:#60a5fa;text-decoration:none}
      a:hover{text-decoration:underline}
      .top-headline{font-size:18px;font-weight:700;color:#fff;margin-bottom:6px}
      .meta{color:#9ca3af;font-size:12px;margin-bottom:10px}
      .source-tag{color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:.06em}
      .footer{text-align:center;color:#6b7280;font-size:11px;margin-top:28px}
      .divider{border-top:1px solid #1f1f1f;margin:16px 0}
    </style>
    """

    trending_html = "".join(f"<span style='background:#1f1f1f;color:#e5e7eb;padding:3px 10px;border-radius:9999px;font-size:12px;margin:3px 6px 3px 0;display:inline-block'>{html.escape(t['name'])}</span>" for t in brief.get("trendingTopics", []))

    top = brief.get("topStory")
    top_html = ""
    if top:
        top_html = f"""
        <div class="section">
          <div class="source-tag">🔥 Top Story</div>
          <div class="top-headline">{html.escape(top['headline'])}</div>
          <div class="meta">{html.escape(date_str)} • {html.escape(top.get('readTime','4 min'))}</div>
          <a href="{html.escape(top['url'])}" target="_blank">Read full article →</a>
        </div>
        """

    cards_html = ""
    for card in brief.get("newsCards", []):
        bullets = "".join(f"<div class='bullet'>• {html.escape(b)}</div>" for b in card["bullets"])
        cards_html += f"""
        <div class="section">
          <div style="font-size:12px;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">{html.escape(card['category'])}</div>
          <div style="font-weight:700;font-size:16px;margin-bottom:8px;color:#fff">{html.escape(card['headline'])}</div>
          {bullets}
          <div style="margin-top:10px"><a href="{html.escape(card['url'])}" target="_blank">Read more →</a></div>
        </div>
        """

    highlights_html = ""
    for h in brief.get("highlights", []):
        bullets = "".join([f"<div class='bullet'>• {html.escape(h['whyItMatters'])}</div>"])
        highlights_html = f"""
        <div class="section" style="background:#0f0f0f;border-left:3px solid #7c3aed">
          <div style="font-weight:700;margin-bottom:6px;color:#fff">💡 Why It Matters — {html.escape(h['topic'])}</div>
          {bullets}
          <div style="margin-top:8px"><a href="{html.escape(h['url'])}" target="_blank">Read more →</a></div>
        </div>
        """

    articles_html = ""
    for a in articles:
        articles_html += f"""
        <div class="bullet" style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <a href="{html.escape(a['url'])}" target="_blank" style="font-weight:600;color:#e5e7eb">{html.escape(a['title'])}</a>
            <div class="source-tag" style="margin-top:2px">{html.escape(a['source'])} • {html.escape(a['timeAgo'])}</div>
          </div>
          <span style="color:#6b7280">↗</span>
        </div>
        """

    breakdown = brief.get("sourceBreakdown", {})
    breakdown_rows = "".join(
        f"<tr><td style='padding:4px 0;color:#d1d5db'>{html.escape(src)}</td><td style='text-align:right;color:#9ca3af'>{pct}%</td></tr>"
        for src, pct in sorted(breakdown.items(), key=lambda x: -x[1])
    )

    leaderboard_items = {
        "Top performer": "Claude Fable 5 leads at 100/100 (Swfte leaderboard)",
        "Best agentic all-rounder": "GPT-5.5 at $5/$30 per 1M tokens",
        "Best price/performance coding": "DeepSeek V4 Pro at <strong>$0.435/$0.87 per 1M</strong> — 5–34x cheaper than closed models",
        "Cheapest viable API": "DeepSeek V4 Flash at <strong>$0.14/$0.28 per 1M</strong>",
        "Longest context": "Llama 4 Scout hits <strong>10M tokens</strong> (unique among frontier models)",
        "Supply chain note": "Google reportedly couldn't fulfill Meta's full Gemini API capacity request in March, disrupting internal AI projects",
    }
    leaderboard_html = "".join(f"<div class='bullet'>• <strong>{k}:</strong> {v}</div>" for k, v in leaderboard_items.items())

    enterprise_items = [
        "Ramen Aura 15.0 — multi-agent assistant for Unreal Engine / Unity game dev",
        "Trintech Flux Agent — automated financial close fluctuation analysis",
        "EZ Texting — full platform overhaul to agentic AI for marketing ops",
        "BreachRx Rex Platform — agentic AI incident command center for cyberattacks",
        "Checksum API Agent — autonomous journey-based API testing in CI/CD",
        "IGC Pharma AHA — agentic AI for Alzheimer's drug discovery, claims 90% research workload reduction",
    ]
    enterprise_html = "".join(f"<div class='bullet'>• {html.escape(x)}</div>" for x in enterprise_items)

    tldr_items = [
        "GPT-5.6 just dropped — focus is agentic long-horizon tasks, pricing is aggressive vs rivals",
        "Build with DeepSeek V4 Pro/Flash if you care about cost-to-reasoning ratio",
        "MCP is back in favor for enterprise integrations; don't ignore it",
        "CLI agents > IDE agents for real shipping velocity",
        "SLMs are production-ready for many agent tasks — not just research toys",
        "The market is <strong>$7.8B</strong> now, projected <strong>$52B</strong> by 2030; Gartner says <strong>40%</strong> of enterprise apps will embed agents by end of 2026",
    ]
    tldr_html = "".join(f"<div class='bullet'>{i}. {x}</div>" for i, x in enumerate(tldr_items, 1))

    return f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">{styles}</head><body>
      <div class="container">
        <div style="text-align:center;margin-bottom:22px">
          <div style="font-size:22px;font-weight:800;letter-spacing:-.02em;color:#fff">Tech Brief</div>
          <div style="color:#9ca3af;font-size:12px">Daily AI/Tech Intelligence — {html.escape(date_str)}</div>
        </div>

        {top_html}

        <div class="section">
          <div class="section-title">⚡ TL;DR for a GenAI dev like you</div>
          {tldr_html}
        </div>

        <div class="section">
          <div class="section-title">🏆 Current LLM Leaderboard Snapshot ({html.escape(date_str)})</div>
          {leaderboard_html}
        </div>

        <div class="section">
          <div class="section-title">🏢 Enterprise Agent Launches This Week</div>
          {enterprise_html}
        </div>

        <div class="section">
          <div class="section-title">📰 All Articles</div>
          {articles_html}
        </div>

        <div class="footer">
          Curated from {len(breakdown)} sources • Last 24 hours • Updated 7:00 AM IST<br>
          <span style="color:#374151">—</span><br>
          <span style="font-size:10px">Open-source • Built with Python + Gmail SMTP</span>
        </div>
      </div>
    </body></html>
    """

# ─── SEND ──────────────────────────────────────────────────────────────────

def send_email(html_content, subject):
    try:
        # Load recipients from file (primary) or env var (fallback)
        recipients = []
        if os.path.exists(RECIPIENT_FILE):
            with open(RECIPIENT_FILE, "r", encoding="utf-8") as f:
                recipients = [addr.strip() for addr in json.load(f) if addr.strip()]
        if not recipients:
            recipients = [addr.strip() for addr in os.getenv("RECIPIENT_EMAIL", "").split(",") if addr.strip()]
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            app_pw = EMAIL_APP_PASSWORD.replace(" ", "")
            server.login(EMAIL_ADDRESS, app_pw)
            server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())

        print(f"[OK] Sent to {len(recipients)} recipient(s)")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

# ─── MAIN ──────────────────────────────────────────────────────────────────

def main():
    print("[*] Fetching feeds...")
    entries = fetch_feeds()
    print(f"[*] {len(entries)} articles found")
    if not entries:
        print("[!] No articles")
        return

    print("[*] Building brief...")
    brief = build_brief(entries)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(brief, f, indent=2, ensure_ascii=False)

    today = datetime.datetime.now().strftime("%B %d, %Y")
    subject = f"Tech Brief — {today}"
    html_body = build_html_email(brief)

    print("[*] Sending...")
    send_email(html_body, subject)

if __name__ == "__main__":
    main()
