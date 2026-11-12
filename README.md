# Milebird website

The site for **Milebird** (App Store name "Mileage Tracker: Milebird"), the automatic mileage tracker for iPhone.
GitHub Pages serves this repo's `main` branch from the root at https://coderalert0.github.io/milebird-site/.
Same layout and build as the Mapsheet and Doorproof sites, copied into this repo (nothing here links into another repo).

## Build and check

```
python3 -m venv .venv && .venv/bin/pip install markdown pillow
.venv/bin/python src/build.py          # writes the pages, sitemap, llms.txt, icons and img/og.png into the root
python3 src/check.py                   # pages, internal links and anchors, titles, descriptions, JSON-LD, sitemap
python3 src/check.py --external        # also every outside link (IRS, Apple, competitors' pricing pages)
```

The build needs macOS (it sizes the icon with `sips` and draws the social card with Helvetica Neue). Edit only `src/`,
`style.css` and `site.js`; every `.html`, `.md`, `sitemap.xml`, `robots.txt`, `llms*.txt`, `icon.png`, `favicon-32.png`,
`img/icon-512.png` and `img/og.png` in the root is generated. Change `UPDATED` in `src/build.py` when facts are rechecked.

| Source | Page |
|---|---|
| `src/pages/home.html` | `index.html` (hero, features, how detection works, free vs Pro, switching, guides, FAQ) |
| `src/pages/support.body.html` | `support.html` (use as the App Store Support URL) |
| `src/pages/privacy.body.html` | `privacy.html` (the Privacy Policy URL) |
| `src/pages/terms.body.html` | `terms.html` (subscription terms; links Apple's standard EULA) |
| `src/pages/guides/*.md` | one guide page each, plus a Markdown copy beside it |

The support address is written by `site.js` (pages show "laddothis at gmail dot com" without JavaScript).

## Where the images go

Only ChatGPT-generated images and the app's own screenshots: no stock photos and no drawn illustrations.

- **App icon (in place).** `src/art/icon-1024.png`, the 1024×1024 icon chosen Nov 11, 2026 (copied from
  `~/milebird-icons/AppIcon-1024.png`). The build makes `icon.png` (180 px: header, hero, apple-touch-icon),
  `favicon-32.png` and `img/icon-512.png` (structured data, social card) from it. To change the icon, replace that one
  file and rebuild.
- **Screenshots (not yet).** Put the app's screenshots (portrait PNG or JPG, any size; the build scales them to 600 px
  wide) in `src/art/shots/`, and next to them a `src/art/shots/shots.json` listing them in order:

  ```json
  [
    {"file": "1-drives.png", "title": "Every drive, logged", "caption": "Sorted with one tap.",
     "alt": "Milebird's Drives list: three drives on Tuesday, one marked Business"},
    {"file": "2-detail.png", "title": "The route and the log line", "caption": "Stops, purpose and the IRS entry.",
     "alt": "A drive's detail screen with its route on a map"}
  ]
  ```

  Write the `alt` text from what each screenshot actually shows. With that file present, the home page gets a
  screenshot gallery right after "What Milebird does" (the `{SHOTS}` spot in `src/pages/home.html`), the structured data
  lists them, and the first one goes on the social card `img/og.png` beside the text. Without it, nothing is shown and
  the pages read complete: the hero carries an HTML example of the drive log, not a picture.

## The App Store link

`APP_ID` in `src/build.py` is empty because the app has no App Store record yet. Until it's set, the pages say "Coming
soon to the App Store" (the nav button reads "Coming soon") and nothing links to the store. Once App Store Connect gives
the app its Apple ID, set `APP_ID = "<digits>"` and rebuild: the Apple badge, "Get the app", the Smart App Banner meta
tag, the store link in llms.txt and the JSON-LD install URL all switch on.

## Keep in step with the app

These pages state what the app does and costs. When the app changes, update them in the same release:

- Prices, the trial and its reminder, Restore Purchases and cancelling: `src/pages/terms.body.html`,
  `src/pages/support.body.html`, the pricing section of `src/pages/home.html`, `FACTS` and the JSON-LD offers in
  `src/build.py`, and the guide `mileiq-price-increase-alternatives.md`.
- What's free and what's Pro (the comparison table and the FAQ on the home page, `FACTS`).
- iCloud sync: `src/pages/privacy.body.html` says Milebird doesn't sync through iCloud; rewrite that paragraph (what's
  synced, and that it uses the user's private CloudKit database) before sync ships.
- Imports from other apps: the home page and guide 3 say Milebird doesn't import other apps' history yet.

Facts from outside sources (the IRS rates and rules, competitors' prices) were checked on Nov 11, 2026; each guide
lists its sources, and competitor prices are dated in the text. Recheck them before changing `UPDATED`.

## Publish (when the owner says so)

Mirrors mapsheet-site: a public repo `coderalert0/<name>-site`, GitHub Pages built from `main` at `/` (legacy build),
HTTPS enforced, custom 404.

```
cd ~/milebird-site
gh repo create coderalert0/milebird-site --public \
  --description "Milebird website: automatic mileage tracker for iPhone" \
  --source=. --remote=origin --push
gh api -X POST repos/coderalert0/milebird-site/pages -f build_type=legacy -f 'source[branch]=main' -f 'source[path]=/'
gh api repos/coderalert0/milebird-site/pages --jq '{status, html_url, source, https_enforced}'
# after the first build (a minute or two):
curl -sI https://coderalert0.github.io/milebird-site/ | head -1
```

Then, as for the other sites: add the property `https://coderalert0.github.io/milebird-site/` in Google Search Console
under coderalert0@gmail.com (the shared verification file `googlebcd67451a2e45ce3.html` is already in the root), submit
`sitemap.xml`, and use `support.html`, `privacy.html` and `terms.html` as the App Store Connect URLs.
