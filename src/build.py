#!/usr/bin/env python3
"""Builds Milebird's site from src/ into the repo root, which GitHub Pages serves from main.

    python3 -m venv .venv && .venv/bin/pip install markdown pillow
    .venv/bin/python src/build.py && python3 src/check.py

Pages: the home page (src/pages/home.html), support, privacy and terms (src/pages/*.body.html) and the guides
(src/pages/guides/*.md, each with a Markdown copy next to its page). Also written: 404.html, sitemap.xml, robots.txt,
llms.txt and llms-full.txt for AI tools, the icons and the social card img/og.png.

Images (README.md says where each goes): the app icon is src/art/icon-1024.png (made with ChatGPT; sips makes the
smaller sizes, so the build needs macOS). App screenshots go in src/art/shots/ with a shots.json that gives each one's
caption and alt text; with no shots.json the home page has no gallery and still reads complete. Set APP_ID once the
App Store record exists: until then the pages say "Coming soon to the App Store" instead of linking to it.
Change UPDATED when a page's facts are rechecked.
"""
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

import markdown
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
ART = ROOT / "src" / "art"
BASE = "https://coderalert0.github.io/milebird-site/"
APP_ID = "6833829535"   # the App Store Connect Apple ID (digits)
APP = f"https://apps.apple.com/us/app/id{APP_ID}" if APP_ID else ""
NAME = "Milebird"
APP_NAME = "Mileage Tracker: Milebird"
ACCENT = (21, 80, 230)   # #1550E6, sampled from the icon
TERMS = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
UPDATED = "2026-11-11"
UPDATED_LONG = date.fromisoformat(UPDATED).strftime("%B %-d, %Y")
DISCLAIMER = ("Milebird is a record-keeping tool, not tax advice: check the rules and rates that apply to you. Milebird is not "
              "affiliated with the IRS, Apple, MileIQ, Everlance, Driversnote or TripLog.")
HOME_TITLE = "Milebird: Automatic Mileage Tracker for iPhone, Free"
HOME_DESCRIPTION = ("Automatic mileage log for iPhone: every drive logged by itself, one-tap business or personal, the IRS rate "
                    "by date. Unlimited tracking free, no account.")
SUMMARY = ("Milebird is an automatic mileage tracker for iPhone. It notices when you start driving and logs each drive by "
           "itself (date, times, where from and to, and miles), so self-employed people and employees who drive for work can "
           "mark drives Business or Personal with one tap and keep an IRS-style mileage log. Unlimited automatic tracking is "
           "free, with no account, and drives stay on the iPhone.")
STATUS = (f"On the App Store: {APP}" if APP else
          "Coming soon to the App Store (not yet available). This site describes the app and its planned prices.")
FACTS = [
    "Free, with no account: unlimited automatic drive detection with no monthly cap; starting or ending a drive by hand and adding a forgotten one; viewing, sorting (Business, Personal, Medical, Charity or Not a drive), editing, splitting and joining every drive; the IRS rate for each drive's date; the Reports tab with the year's business miles and a CSV; CSV export, CSV import from another app and a backup file any time; one vehicle; tracking-health alerts and a Diagnostics screen.",
    "Milebird Pro costs $6.99 a month, $49.99 a year (new subscribers get a 14-day free trial on the yearly plan, with a reminder 2 days before it ends) or $119.99 once for Lifetime, in the US. It adds auto-classify rules (work hours, named places, the IRS commute rule), IRS-ready PDF logs and employer reimbursement reports, several vehicles with odometer readings, clients and custom rates, and iCloud sync.",
    "Drives never lock: free users and anyone whose Pro ends keep every drive viewable, editable and exportable. Price promise: subscribers keep their price for as long as they stay subscribed; any price change for new buyers is announced in the app 30 days ahead.",
    "Detection: the GPS is off between drives. iOS wakes Milebird through a geofence of about 150 meters around where the car parked, significant-location changes, visits and Motion & Fitness. It checks for up to 3 minutes, then records the route with GPS while you drive. Stops shorter than the stop timeout (4 minutes by default, 1 to 15 in Settings) stay in one drive. Drives from about 0.2 miles count. Walks, runs, bike rides, flights and a parked phone aren't logged; rides that look like a train, a bus or someone else's car are flagged for the user.",
    "Distances come from the driven GPS track, with bad fixes filtered out. Stretches without GPS (a tunnel, a late wake-up) are drawn straight and marked as estimated.",
    "IRS standard mileage rates by date: 2026 business 72.5 cents a mile from January 1 to June 30 and 76 cents from July 1, 2026 (IRS Announcement 2026-11); medical and military moving 20.5 then 23.5 cents; charity 14 cents. Each drive uses the rate for its date; the table is editable.",
    "CSV columns: date, start, end, from, to, miles, category, purpose, vehicle, rate (cents a mile) and value.",
    "Privacy: no account, no server, no analytics, no advertising and no third-party code. Location and motion are processed on the iPhone; drives are stored there and in the iPhone's own iCloud or computer backup, and, with Pro iCloud sync turned on, in the user's own private iCloud database (CloudKit). A drive's map is drawn with Apple Maps, and addresses for unnamed places come from Apple's geocoder. App Store privacy label: Data Not Collected.",
    "Car signal, Lock Screen and Siri: CarPlay, or the Bluetooth audio of a car marked as the user's, helps start and end drives. A Live Activity shows a drive in progress on the Lock Screen and in the Dynamic Island. Siri and Shortcuts can start or end a drive, sort the last drive and say this month's business miles.",
    "Regions: United States (IRS rates, miles), Canada (CRA tiers, 73 cents a km for the first 5,000 km in 2026 and 67 after, kilometres), United Kingdom (HMRC 55p a mile for the first 10,000 business miles of the tax year from 6 April 2026, 25p after) and Australia (ATO 91 cents a km for 2026–27, up to 5,000 km per car, kilometres), each counted through its own tax year. Each region exports its authority's logbook (the CRA's in English or French, HMRC's, the ATO's car log and 12-week logbook): CSV free, PDF with Pro.",
    "Support: email, answered by a person, usually within one business day; Email support in the Diagnostics tab fills in the Diagnostics summary and recent log.",
    "Runs on iPhone with iOS 17 or later, in English and French (Canada). " + STATUS,
]


def parse(path):
    _, head, body = path.read_text().split("---\n", 2)
    meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
    meta["slug"] = path.stem
    meta["related"] = [s.strip() for s in meta.get("related", "").split(",") if s.strip()]
    meta["body"] = body.strip()
    faq_block = re.search(r"## Frequently asked questions\n(.*?)(?=\n## |\Z)", body, re.S)
    meta["faqs"] = re.findall(r"### (.+?)\n\n(.+?)(?=\n\n###|\Z)", faq_block.group(1).strip(), re.S) if faq_block else []
    source_block = re.search(r"## Sources\n(.*)", body, re.S)
    meta["sources"] = re.findall(r"- \[(.+?)\]\((.+?)\)", source_block.group(1)) if source_block else []
    return meta


def render(text):
    md = markdown.Markdown(extensions=["tables", "sane_lists", "toc"], extension_configs={"toc": {"toc_depth": "2"}})
    out = md.convert(text).replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out, [(t["id"], t["name"]) for t in md.toc_tokens]


def plain(text):
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def jsonld(data):
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


# ---------- Images: the icon (sips) and the app's screenshots ----------

def sips(src, size, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["sips", "-s", "format", "png", "-z", str(size), str(size), str(src), "--out", str(out)],
                   check=True, capture_output=True)


ICON_SRC = ART / "icon-1024.png"
if ICON_SRC.exists():
    sips(ICON_SRC, 180, ROOT / "icon.png")              # apple-touch-icon, header and hero
    sips(ICON_SRC, 32, ROOT / "favicon-32.png")         # browser tab
    sips(ICON_SRC, 512, ROOT / "img" / "icon-512.png")  # structured data and the social card
HAS_ICON = (ROOT / "icon.png").exists()

SHOTS = []   # [{"file", "title", "caption", "alt", "src", "w", "h"}], from src/art/shots/shots.json
shots_json = ART / "shots" / "shots.json"
if shots_json.exists():
    for s in json.loads(shots_json.read_text()):
        im = Image.open(ART / "shots" / s["file"]).convert("RGB")
        w = 600
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        out = ROOT / "img" / "shots" / (Path(s["file"]).stem + ".jpg")
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, quality=84, optimize=True, progressive=True)
        SHOTS.append({**s, "src": f"img/shots/{out.name}", "w": im.width, "h": im.height})

PUBLISHER = {"@type": "Organization", "name": NAME, "url": BASE}
if HAS_ICON:
    PUBLISHER["logo"] = BASE + "img/icon-512.png"


def social_card():
    """img/og.png: 1200x630, cool paper, the icon, the name and the promise, beside the first screenshot (or the icon)."""
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), (245, 247, 251))
    d = ImageDraw.Draw(card)
    font = lambda size, bold=True: ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=1 if bold else 0)

    def rounded(img, size, radius):
        img = img.convert("RGB").resize(size, Image.LANCZOS)
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
        return img, mask

    def shadowed(img, mask, xy, radius):
        shadow = Image.new("L", (W, H), 0)
        x, y = xy
        ImageDraw.Draw(shadow).rounded_rectangle((x + 6, y + 18, x + img.width + 6, y + img.height + 18), radius, fill=80)
        card.paste((196, 204, 222), (0, 0), shadow.filter(ImageFilter.GaussianBlur(22)))
        card.paste(img, xy, mask)

    x = 72
    if HAS_ICON:
        icon, mask = rounded(Image.open(ROOT / "img" / "icon-512.png"), (96, 96), 22)
        card.paste(icon, (72, 76), mask)
        x = 186
    d.text((x, 96), NAME, font=font(56), fill=(15, 26, 46))
    y = 232
    for line, color in (("Every drive logged,", (15, 26, 46)), ("without lifting a finger.", ACCENT)):
        d.text((72, y), line, font=font(54), fill=color)
        y += 68
    d.text((72, y + 26), "Automatic mileage tracker for iPhone.", font=font(30, False), fill=(85, 96, 120))
    d.text((72, y + 66), "Unlimited tracking free. No account.", font=font(30, False), fill=(85, 96, 120))
    if SHOTS:
        shot = Image.open(ROOT / SHOTS[0]["src"])
        sw = 300
        img, mask = rounded(shot, (sw, round(shot.height * sw / shot.width)), 36)
        shadowed(img, mask, (W - sw - 80, 48), 36)
    elif HAS_ICON:
        img, mask = rounded(Image.open(ROOT / "img" / "icon-512.png"), (300, 300), 68)
        shadowed(img, mask, (W - 300 - 96, (H - 300) // 2 - 10), 68)
    card.save(ROOT / "img" / "og.png", optimize=True)


social_card()

# ---------- Page shell ----------

if APP:
    GET = f'<a class="badge" href="{APP}"><img src="{{root}}img/app-store-badge.svg" alt="Download on the App Store" width="150" height="50"></a>'
else:
    GET = '<span class="soon">Coming soon to the App Store<small>For iPhone, iOS 17 or later</small></span>'


def get_button(root=""):
    return GET.replace("{root}", root)


def page(slug, title, description, body, *, schema=(), kind="article", current="", root="", markdown_twin=False,
         robots="index,follow,max-snippet:-1,max-image-preview:large"):
    url = BASE if slug == "index" else f"{BASE}{slug}.html"
    e = html.escape
    alternate = f'\n<link rel="alternate" type="text/markdown" href="{root}{slug}.md">' if markdown_twin else ""
    ld = "\n".join(jsonld(item) for item in schema)
    here = lambda name: ' aria-current="page"' if name == current else ""
    home = root or "./"
    icons = (f'\n<link rel="icon" type="image/png" sizes="32x32" href="{root}favicon-32.png">'
             f'\n<link rel="apple-touch-icon" href="{root}icon.png">') if HAS_ICON else ""
    brand_img = lambda size: f'<img src="{root}icon.png" alt="" width="{size}" height="{size}">' if HAS_ICON else ""
    itunes = f'\n<meta name="apple-itunes-app" content="app-id={APP_ID}">' if APP_ID else ""
    cta = (f'<a class="nav-cta" href="{APP}">Get the app</a>' if APP else f'<a class="nav-cta" href="{home}#get">Coming soon</a>')
    store_link = f'<a href="{APP}">App Store</a>' if APP else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">{alternate}
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f5f7fb" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0b1020" media="(prefers-color-scheme: dark)">{itunes}
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Milebird, the automatic mileage tracker for iPhone: every drive logged, without lifting a finger">
<meta name="twitter:card" content="summary_large_image">{icons}
<link rel="stylesheet" href="{root}style.css">
<link rel="alternate" type="text/plain" title="llms.txt" href="{root}llms.txt">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="topbar-in">
    <a class="brand" href="{home}">{brand_img(34)}<span>{NAME}</span></a>
    <nav class="nav" aria-label="Site">
      <a class="hide-sm" href="{home}#detection">How it works</a>
      <a class="hide-sm" href="{home}#pricing">Pricing</a>
      <a class="hide-sm" href="{home}#guides"{here("guides")}>Guides</a>
      <a href="{root}support.html"{here("support")}>Support</a>
      {cta}
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer>
  <div class="in">
    <div class="foot-about">
      <a class="brand" href="{home}">{brand_img(28)}<span>{NAME}</span></a>
      <p>The automatic mileage tracker for iPhone.</p>
      <p>© 2026 {NAME}. {DISCLAIMER}</p>
    </div>
    <nav aria-label="Guides"><p class="foot-title">Guides</p>{FOOTER_GUIDES.replace('href="', f'href="{root}')}</nav>
    <nav aria-label="App"><p class="foot-title">App</p>{store_link}<a href="{root}support.html">Support</a><a href="{root}privacy.html"{here("privacy")}>Privacy Policy</a><a href="{root}terms.html"{here("terms")}>Terms of Use</a><a href="{root}llms.txt">llms.txt</a></nav>
  </div>
</footer>
<script src="{root}site.js"></script>
</body>
</html>
"""


def guide_page(g, by_slug):
    body_md = re.sub(r"\n## Sources\n.*", "", g["body"], flags=re.S)
    content, headings = render(body_md)
    url = f'{BASE}{g["slug"]}.html'
    e = html.escape
    sources = "".join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in g["sources"])
    related = "".join(f'<li><a href="{s}.html">{e(by_slug[s]["h1"])}</a></li>' for s in g["related"])
    toc = "".join(f'<li><a href="#{i}">{e(n)}</a></li>' for i, n in headings)
    body = f"""<div class="guide">
<nav class="crumbs" aria-label="Breadcrumb"><a href="./">Home</a> <span aria-hidden="true">/</span> <a href="./#guides">Guides</a> <span aria-hidden="true">/</span> <span>{e(g["nav"])}</span></nav>
<article>
<h1>{e(g["h1"])}</h1>
<p class="updated">Checked against its sources on <time datetime="{UPDATED}">{UPDATED_LONG}</time></p>
<div class="answer"><h2>Short answer</h2><p>{e(g["answer"])}</p></div>
<nav class="toc" aria-label="On this page"><p class="foot-title">On this page</p><ul>{toc}</ul></nav>
{content}
<aside class="app-cta">
  <div><h2>Every drive, logged by itself</h2><p>Milebird logs your drives automatically, values each at the IRS rate for its date, and lets you sort them with one tap. Unlimited tracking free, no account, on iPhone.</p></div>
  {get_button()}
</aside>
<section class="sources"><h2>Sources</h2><ul>{sources}</ul><p class="muted">Guides summarize public sources and aren't tax advice. Check the rules that apply to you, or ask a tax professional.</p></section>
<section class="related"><h2>Related guides</h2><ul>{related}</ul></section>
</article>
</div>"""
    crumbs = [("Home", BASE), ("Guides", BASE + "#guides"), (g["nav"], url)]
    article = {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["description"],
               "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": url, "image": BASE + "img/og.png",
               "author": PUBLISHER, "publisher": PUBLISHER, "inLanguage": "en-US", "citation": [u for _, u in g["sources"]]}
    schema = [article, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}]
    if g["faqs"]:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in g["faqs"]]})
    return page(g["slug"], g["title"], g["description"], body, schema=schema, current="guides", markdown_twin=True)


def guide_markdown(g):
    body = re.sub(r"\]\((?!https?:)([a-z0-9-]+)\.html(#[a-z0-9-]+)?\)", rf"]({BASE}\1.md)", g["body"])
    return f"""# {g["h1"]}

> {g["answer"]}

Source page: {BASE}{g["slug"]}.html
Checked against its sources on {UPDATED_LONG}. Published by {NAME}, an automatic mileage tracker for iPhone. Not tax advice.

{body}
"""


def faq_schema(text):
    pairs = re.findall(r"<details><summary>(.+?)</summary><p>(.+?)</p></details>", text)
    return pairs, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in pairs]}


# ---------- Guides ----------

guides = [parse(p) for p in sorted((PAGES / "guides").glob("*.md"))]
order = ["irs-mileage-log-requirements", "how-to-track-mileage-automatically", "mileiq-price-increase-alternatives"]
guides.sort(key=lambda g: order.index(g["slug"]) if g["slug"] in order else len(order))
by_slug = {g["slug"]: g for g in guides}
FOOTER_GUIDES = "".join(f'<a href="{g["slug"]}.html">{html.escape(g["nav"])}</a>' for g in guides)

for g in guides:
    (ROOT / f'{g["slug"]}.html').write_text(guide_page(g, by_slug))
    (ROOT / f'{g["slug"]}.md').write_text(guide_markdown(g))

# ---------- Home ----------

cards = "".join(f'<li><a href="{g["slug"]}.html"><strong>{html.escape(g["h1"])}</strong><span>{html.escape(g["description"])}</span></a></li>' for g in guides)
if SHOTS:
    figures = "".join(f'<figure><img src="{s["src"]}" alt="{html.escape(s["alt"])}" loading="lazy" width="{s["w"]}" height="{s["h"]}">'
                      f'<figcaption><strong>{html.escape(s["title"])}</strong>{html.escape(s["caption"])}</figcaption></figure>' for s in SHOTS)
    shots_html = f'<section class="wrap" aria-label="Screenshots"><div class="shots">{figures}</div></section>\n'
else:
    shots_html = ""   # screenshots: drop them in src/art/shots/ with shots.json (see README.md)
hero_icon = '<img class="hero-icon" src="icon.png" alt="Milebird app icon" width="88" height="88">' if HAS_ICON else ""
home = ((PAGES / "home.html").read_text().replace("{GET}", get_button()).replace("{GUIDES}", f'<ul class="guides">{cards}</ul>')
        .replace("{SHOTS}", shots_html).replace("{HERO_ICON}", hero_icon))
faqs, home_faq = faq_schema(home)
app_ld = {"@context": "https://schema.org", "@type": "MobileApplication", "name": APP_NAME, "alternateName": NAME, "url": BASE,
          "operatingSystem": "iOS 17.0 or later", "applicationCategory": "FinanceApplication", "description": SUMMARY,
          "featureList": ["Automatic drive detection with no monthly cap", "One-tap Business or Personal", "Mark a whole day, with Undo",
                          "IRS standard mileage rate by date, including the July 1, 2026 change", "CSV export and backup file",
                          "Tracking-health alerts", "Diagnostics", "Split and join drives at stops",
                          "Auto-classify rules (Pro)", "IRS-ready PDF and reimbursement reports (Pro)",
                          "Several vehicles and odometer readings (Pro)", "iCloud sync (Pro)"],
          "inLanguage": "en", "publisher": PUBLISHER,
          "offers": [{"@type": "Offer", "name": "Milebird (free, unlimited automatic tracking)", "price": "0", "priceCurrency": "USD"},
                     {"@type": "Offer", "name": "Milebird Pro, monthly", "price": "6.99", "priceCurrency": "USD"},
                     {"@type": "Offer", "name": "Milebird Pro, yearly", "price": "49.99", "priceCurrency": "USD"},
                     {"@type": "Offer", "name": "Milebird Pro, lifetime", "price": "119.99", "priceCurrency": "USD"}]}
if APP:
    app_ld.update(installUrl=APP, downloadUrl=APP)
if HAS_ICON:
    app_ld["image"] = BASE + "img/icon-512.png"
if SHOTS:
    app_ld["screenshot"] = [BASE + s["src"] for s in SHOTS]
home_schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE, "description": HOME_DESCRIPTION,
                "publisher": PUBLISHER, "inLanguage": "en-US"}, app_ld, home_faq]
(ROOT / "index.html").write_text(page("index", HOME_TITLE, HOME_DESCRIPTION, home, schema=home_schema, kind="website", current="home"))

# ---------- Support, privacy, terms (the app and App Store Connect link to these URLs, so they keep them) ----------

DOCS = {
    "support": ("Milebird Support: Help and Troubleshooting", "Help with Milebird: permissions, Low Power Mode, missing drives, exporting, a new iPhone, and Pro billing. A person answers by email."),
    "privacy": ("Privacy Policy · Milebird", "Milebird has no account, no server and no analytics: your location, motion and drives are processed and stored on your iPhone."),
    "terms": ("Terms of Use · Milebird", "Milebird's terms: what's free, Milebird Pro subscriptions, trials, auto-renewal and cancelling, the price promise, and limits."),
}
bodies = {}
for slug, (title, description) in DOCS.items():
    body = (PAGES / f"{slug}.body.html").read_text()
    bodies[slug] = body
    schema = [{"@context": "https://schema.org", "@type": "WebPage", "name": title.replace(" · ", " – "), "url": f"{BASE}{slug}.html",
               "dateModified": UPDATED, "publisher": PUBLISHER, "inLanguage": "en-US",
               "about": {"@type": "MobileApplication", "name": APP_NAME, "url": BASE}}]
    if slug == "support":
        schema.append(faq_schema(body)[1])
    (ROOT / f"{slug}.html").write_text(page(slug, title, description, f'<div class="doc">\n{body}</div>', schema=schema, current=slug))

# 404 is served at any depth, so its links are absolute.
missing = ('<div class="doc"><h1>Page not found</h1><p>That page has moved or never existed.</p><p><a href="/milebird-site/">Go to '
           'Milebird\'s home page</a>, read <a href="/milebird-site/irs-mileage-log-requirements.html">what an IRS mileage log must '
           'show</a>, or <a href="/milebird-site/support.html">get support</a>.</p></div>')
(ROOT / "404.html").write_text(page("404", f"Page not found · {NAME}", "This page could not be found.", missing, robots="noindex", root="/milebird-site/"))

# ---------- Sitemap, robots, llms ----------

urls = ([(BASE, "1.0")] + [(f'{BASE}{g["slug"]}.html', "0.8") for g in guides]
        + [(f"{BASE}support.html", "0.6"), (f"{BASE}privacy.html", "0.3"), (f"{BASE}terms.html", "0.3")])
entries = "".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED}</lastmod><priority>{p}</priority></url>\n" for u, p in urls)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n')
# robots.txt only counts at a host's root, so on github.io this copy is a pointer for tools that read it here; the sitemap
# is submitted to the search engines directly.
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot",
           "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot", "CCBot", "DuckAssistBot", "meta-externalagent"]
(ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_BOTS)
                                 + f"Sitemap: {BASE}sitemap.xml\n")

facts = "\n".join(f"- {f}" for f in FACTS)
links = "\n".join(f'- [{g["h1"]}]({BASE}{g["slug"]}.md): {g["description"]}' for g in guides)
store_line = f"- [App Store listing]({APP}): {APP_NAME}, for iPhone, iOS 17 or later\n" if APP else ""
(ROOT / "llms.txt").write_text(f"""# {NAME}

> {SUMMARY}

{DISCLAIMER} Facts on this site were checked on {UPDATED_LONG}. When citing a guide, link its page.

## Key facts

{facts}

## Guides

{links}

## App

{store_line}- [Home page]({BASE}): What Milebird does, how detection works, free and Pro, switching, questions
- [Support]({BASE}support.html): Permissions, Low Power Mode, missing drives, exporting, a new iPhone, billing
- [Privacy Policy]({BASE}privacy.html): No account, no server, no analytics; location and drives stay on the iPhone
- [Terms of Use]({BASE}terms.html): What's free, Pro subscriptions and trials, the price promise, not tax advice; on top of Apple's standard license agreement ({TERMS})

## Optional

- [Full text]({BASE}llms-full.txt): The facts, the questions and answers, every guide and the privacy policy in one Markdown file
""")


def doc_markdown(body):
    md = re.sub(r"<li>", "- ", body)
    md = re.sub(r"<h2>(.+?)</h2>", r"## \1", md)
    md = re.sub(r"<details><summary>(.+?)</summary><p>(.+?)</p></details>", r"### \1\n\2", md)
    md = re.sub(r"<h1>(.+?)</h1>", "", md)
    md = "\n".join(l.strip() for l in plain(md.replace("laddothis at gmail dot com", "laddothis@gmail.com")).splitlines() if l.strip())
    return re.sub(r"\n(##+ )", r"\n\n\1", md)


qa = "\n\n".join(f"### {plain(q)}\n\n{plain(a)}" for q, a in faqs)
full = [f"# {NAME}\n\n> {SUMMARY}\n\n{DISCLAIMER} Checked on {UPDATED_LONG}. Source: {BASE}\n\n## Key facts\n\n{facts}\n\n## Questions and answers\n\n{qa}"]
full += [guide_markdown(g) for g in guides]
full.append(f"# Milebird support\n\nSource page: {BASE}support.html\n\n{doc_markdown(bodies['support'])}\n")
full.append(f"# Milebird privacy policy\n\nSource page: {BASE}privacy.html\n\n{doc_markdown(bodies['privacy'])}\n")
(ROOT / "llms-full.txt").write_text("\n\n---\n\n".join(full))
(ROOT / ".nojekyll").write_text("")
print(f"built home, support, privacy, terms, 404 and {len(guides)} guides; icon: {'yes' if HAS_ICON else 'no'}; screenshots: {len(SHOTS)}; App Store link: {'yes' if APP else 'not yet (APP_ID empty)'}")
