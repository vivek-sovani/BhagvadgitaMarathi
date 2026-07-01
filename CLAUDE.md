# CLAUDE.md — गीता-ज्ञानेश्वरी Project Guide

Marathi Bhagavad Gita PWA deployed on GitHub Pages at `https://vivek-sovani.github.io/BhagvadgitaMarathi/`. Presents 18 chapters (अध्याय), each with multiple concepts (संकल्पना), combining infographic images, PDFs, modern Marathi stories (कथा), Dnyaneshwari commentary (विवेचन), and audio (श्रवण).

---

## Key Files

| File | Role |
|---|---|
| `js/data.js` | `GITA_DATA` — all 18 chapters + concept metadata (name, emoji, summary, available flag) |
| `js/triggers.js` | `GITA_TRIGGERS` — hook paragraphs shown before user picks a section |
| `js/stories.js` | `GITA_STORIES` — structured katha story data or `kathaHtmlUrl` for combined adhyays |
| `js/content.js` | `GITA_CONTENT` — vivechan/Dnyaneshwari text per concept (~845KB, parsed by adhyay.js) |
| `js/adhyay.js` | Main SPA controller — all concept/section rendering, PDF, navigation |
| `js/home.js` | Home chapter grid + daily concept picker |
| `js/share.js` | `window.initShareButton()` — Web Share API + WhatsApp/clipboard fallback |
| `adhyay.html` | Chapter/concept SPA shell |
| `sw.js` | Service worker — cache name `gita-v28` (bump when cached files change) |
| `manifest.json` | PWA manifest — scope `/BhagvadgitaMarathi/`, lang `mr`, theme `#9c4a10` |
| `scripts/send_daily_concept.py` | Daily email — run by GitHub Actions at 4:45 AM IST |
| `build_sankalpana.py` | Builds `sankalpana/*.html` from `content/sankalpana/*.md` |

---

## Data Structures

### GITA_DATA adhyay object
```js
{ id: 1, number: "१", name: "अर्जुनविषादयोग", emoji: "😔", available: true,
  shlokas: true,           // optional — shows the full-shloka banner (see below)
  summary: "...",
  concepts: [{ id: 1, emoji: "🏹", name: "...", tagline: "..." }] }
```
The optional `shlokas: true` flag makes the "मूळ श्लोक व मराठी अर्थ" banner appear on the adhyay
cover page, linking to `shlokas/adhyay-N.html`. Set it only after that file is uploaded.

### GITA_TRIGGERS concept object
```js
{ paras: ["HTML para 1", "HTML para 2"], cta: "closing line" }
```
Inline `<strong>/<em>` allowed. Keyed as `GITA_TRIGGERS[adhyayId][String(conceptId)]`.

### GITA_STORIES concept object
Two modes:
- **Combined adhyays 8–18**: `{ kathaHtmlUrl: "assets/adhyay-N/concept-M-katha.html" }` — embedded in iframe
- **Adhyays 1–7**: `{ shloka, conceptSummary, audioUrl?, imageUrl?, pdfUrl?, story: { scene, characters, body[], turningPoint, gitaConnect, reflection, sankalp } }`

Story `body` item types: `para`, `dialogue`, `inner-thought`, `hbox`, `contrast`, `diary`, `layers`, `grid`, `traits`, `vastra`.

### GITA_CONTENT raw text markers (parsed by `renderConceptText`)
- `📖` → श्लोक block
- `🟧` → ज्ञानेश्वरी block
- `💡` → highlight/question
- `🌱` → संकल्प block

---

## Architecture Notes

### Combined vs Non-Combined Adhyays
```js
const isCombinedAdhyay = (adhyayId >= 8 && adhyayId <= 18);
```
- **Adhyays 1–7**: Section menu shows 2–3 cards (विवेचन + कथा + श्रवण). Each has separate content.js text + stories.js structured data.
- **Adhyays 8–18**: Concept landing goes directly to `katha` section (which contains a merged vivechan + katha HTML via iframe). The vivechan card is hidden.

### Navigation
- URL: `adhyay?id=N` (cover), `adhyay?id=N&concept=M` (concept)
- `history.pushState` + `popstate` — browser back works correctly within the SPA
- Share URLs use `/c/N/M/` OG shim pages (all 18 adhyays have shims)

### Sections
Three sections per concept: `vivechan`, `katha`, `shravan`. `showSection(name)` / `showSectionMenu()` control visibility.

### Font Size
Persisted in `localStorage['gita-fontsize']` as `'small'|'normal'|'large'`. Applied as `document.body.dataset.fontsize` and synced into katha iframes.

---

## Asset Conventions

Each `assets/adhyay-N/` folder:
- `adhyay.pdf` — full chapter PDF (shown on chapter cover page)
- `summary.jpg` — chapter cover image
- `concept-M.jpg` — concept infographic (fallback chain: `.jpg → .jpeg → .png`)
- `concept-M.pdf` — concept PDF (right panel carousel)
- `concept-M-katha.html` — standalone katha HTML (combined adhyays)
- `concept-M-katha.pdf` — katha PDF (optional, older adhyays)
- `concept-M-shravan.m4a` — audio (optional)
- `README.txt` — manual notes on asset readiness

---

## Daily Email System

- **WhatsApp post files**: `adhyay1-whatsapp-links.md` … `adhyay13-whatsapp-links.md`
- Blocks separated by `━━━━━━━━━━━━━━━━━━━━━━━`
- `START_DATE = date(2026, 4, 20)` in `send_daily_concept.py` — index 0
- Current position (2026-06-29): index 70 = adhyay 8, concept 3
- Email contains: trigger text (amber box) + WhatsApp post block
- Secrets: `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD` (GitHub Actions secrets)
- Schedule: `23:15 UTC` = `4:45 AM IST`

---

## Sankalpana

70+ standalone concept pages in `sankalpana/`. Source: `content/sankalpana/*.md`. Build: `python3 build_sankalpana.py`. Each page has `window.autoInitSankalpanaShare()` for sharing.

---

## Full-adhyay Shlokas (मूळ श्लोक + मराठी अर्थ)

Self-contained per-chapter pages at `shlokas/adhyay-N.html` — every Sanskrit shloka with a plain
Marathi meaning, in the site's saffron theme (generated via the `gita-adhyay-html` skill). Linked
from a banner on the adhyay cover page (`#shloka-banner` in `adhyay.html`), shown only when the
adhyay has `shlokas: true` in `GITA_DATA`. The banner uses same-tab navigation (browser Back
returns to the adhyay). **To add one**: upload `shlokas/adhyay-N.html`, set `shlokas: true` on that
adhyay in `js/data.js`, and bump the SW cache.

---

## Devanagari Numerals

`toDevNum(n)` in `adhyay.js` converts Arabic → Devanagari (`1` → `१`). Always display Devanagari numerals for adhyay/concept numbers in the UI. Data keys in JS objects use plain integers or strings of Arabic numerals.

---

## When Making Changes

- **New concept content**: Add to `GITA_CONTENT` (content.js), `GITA_TRIGGERS` (triggers.js), `GITA_STORIES` (stories.js), and add assets to `assets/adhyay-N/`.
- **New WhatsApp post**: Add a block to the appropriate `adhyayN-whatsapp-links.md` using the separator format.
- **New katha HTML** (combined adhyay): Create `assets/adhyay-N/concept-M-katha.html`, reference via `kathaHtmlUrl` in stories.js.
- **New full-adhyay shlokas page**: Upload `shlokas/adhyay-N.html`, set `shlokas: true` on that adhyay in `js/data.js`, bump SW cache.
- **SW cache change**: Bump `gita-v28` → `gita-v29` (or next) in `sw.js`.
- **New sankalpana concept**: Add markdown to `content/sankalpana/`, add slug to `SLUGS` list in `build_sankalpana.py`, run the build script.
- **OG shim pages**: Run `scripts/generate_adhyay_shims.py` or `generate_missing_shims.py` after adding new concepts.

---

## Local Dev

```sh
python3 serve.py   # or ./serve.sh
```

Opens a local server. GitHub Pages serves the site from the `main` branch root.
