#!/usr/bin/env python3
"""Fails if the built site has a broken page, broken internal link or anchor, or invalid metadata.

    python3 src/check.py            checks the built files
    python3 src/check.py --external also checks every outside link
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://coderalert0.github.io/milebird-site/"
PREFIX = "/milebird-site/"
errors = []


class Page(HTMLParser):
    void = {"meta", "link", "img", "br", "hr", "input", "source"}

    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name = name
        self.stack, self.links, self.ids, self.ld, self.title, self.text = [], [], [], [], "", []
        self.h1 = 0
        self.in_ld = self.in_title = False
        self.desc = self.canonical = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in self.void:
            self.stack.append(tag)
        if "id" in a:
            self.ids.append(a["id"])
        if tag in ("a", "link", "img", "script"):
            self.links.append(a.get("href") or a.get("src") or "")
        if tag == "img" and "alt" not in a:
            errors.append(f"{self.name}: image without alt")
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.in_title = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self.in_ld = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_ld = False
        if tag in self.void:
            return
        if not self.stack or self.stack.pop() != tag:
            errors.append(f"{self.name}: mismatched </{tag}>")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_ld:
            self.ld.append(data)
        else:
            self.text.append(data)


outside = set()
sitemap = {e.text for e in ET.parse(ROOT / "sitemap.xml").getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
# Search Console proves ownership with this file, so it stays in place and is not a page.
pages = sorted(p for p in ROOT.glob("*.html") if not p.name.startswith("google"))
parsed = {}
for path in pages:
    p = Page(path.name)
    p.feed(path.read_text())
    parsed[path.name] = p

for name, p in parsed.items():
    text = (ROOT / name).read_text()
    if p.stack:
        errors.append(f"{name}: unclosed tags {p.stack[-3:]}")
    if p.h1 != 1:
        errors.append(f"{name}: {p.h1} h1 tags")
    if len(p.ids) != len(set(p.ids)):
        errors.append(f"{name}: duplicate ids {sorted({i for i in p.ids if p.ids.count(i) > 1})}")
    if not 20 <= len(p.title) <= 75:
        errors.append(f"{name}: title is {len(p.title)} characters")
    if not p.desc or not 25 <= len(p.desc) <= 175:
        errors.append(f"{name}: description is {len(p.desc or '')} characters")
    if "terms.html" not in text or "privacy.html" not in text:
        errors.append(f"{name}: missing the Terms of Use or Privacy Policy link")
    words = " ".join(p.text)
    for marker in ("TODO", "FILL IN", "PLACEHOLDER", "Lorem", "{GET}", "{GUIDES}", "{SHOTS}", "{HERO_ICON}", "{APP}"):
        if marker in words or marker in text:
            errors.append(f"{name}: leftover placeholder {marker!r}")
    for block in p.ld:
        try:
            json.loads(block)
        except ValueError as e:
            errors.append(f"{name}: bad JSON-LD: {e}")
    if name != "404.html" and p.canonical not in sitemap:
        errors.append(f"{name}: canonical {p.canonical} is not in the sitemap")
    if name != "404.html" and not p.ld:
        errors.append(f"{name}: no JSON-LD")
    for link in p.links:
        if link.startswith("http"):
            outside.add(link)
            continue
        if link.startswith("mailto:"):
            continue
        target, _, anchor = link.partition("#")
        if link.startswith(PREFIX):
            target = target[len(PREFIX):] or "index.html"   # 404.html links absolutely
        elif target == "":
            target = name                                   # an anchor on this page
        elif target == "./":
            target = "index.html"
        resolved = ROOT / target
        if resolved.is_dir():
            resolved = resolved / "index.html"
        if not resolved.exists():
            errors.append(f"{name}: broken link {link}")
        elif anchor and resolved.suffix == ".html" and resolved.name in parsed and anchor not in parsed[resolved.name].ids:
            errors.append(f"{name}: link {link} points at a missing anchor")

for url in sitemap:
    path = url.replace(BASE, "") or "index.html"
    if not (ROOT / path).exists():
        errors.append(f"sitemap: {url} has no file")

# The app and App Store Connect link to these, so they must keep working.
for required in ("index.html", "support.html", "privacy.html", "terms.html", "404.html", "robots.txt", "llms.txt", "llms-full.txt",
                 "sitemap.xml", "img/og.png", ".nojekyll", "site.js", "style.css"):
    if not (ROOT / required).exists():
        errors.append(f"missing {required}")
for name in ("support.html", "privacy.html", "terms.html"):
    if '<span class="email">' not in (ROOT / name).read_text():
        errors.append(f"{name}: the support address is gone")
if "stdeula" not in (ROOT / "terms.html").read_text():
    errors.append("terms.html: no link to Apple's standard EULA")
for md in ROOT.glob("*.md"):
    if md.name != "README.md" and not (ROOT / md.with_suffix(".html").name).exists():
        errors.append(f"{md.name}: Markdown copy without a page")
for url in re.findall(r"\((https://coderalert0\.github\.io/milebird-site/[^)]+)\)", (ROOT / "llms.txt").read_text()):
    if not (ROOT / url.replace(BASE, "")).exists():
        errors.append(f"llms.txt: broken link {url}")

if "--external" in sys.argv:
    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
    for url in sorted(u for u in outside if "coderalert0.github.io" not in u and "schema.org" not in u):
        try:
            code = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": agent}), timeout=25).status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = repr(e)[:60]
        if code != 200:
            print(f"  outside link {code}: {url}")

print(f"checked {len(pages)} pages, {len(sitemap)} sitemap URLs, {len(outside)} outside links")
for error in errors:
    print("ERROR", error)
sys.exit(1 if errors else 0)
