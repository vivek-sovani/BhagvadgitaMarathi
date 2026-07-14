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
| `js/notify.js` | Daily sankalpana notification engine — settings modal (injected into `#mobile-nav`) + `showNotification` |
| `js/sankalpana-list.js` | Auto-generated `{slug, title}` list for all sankalpana pages, written by `build_sankalpana.py` |
| `js/home.js` | Home chapter grid + daily concept picker |
| `js/share.js` | `window.initShareButton()` — Web Share API + WhatsApp/clipboard fallback |
| `adhyay.html` | Chapter/concept SPA shell |
| `build_prasang.py` | Builds `prasang/*.html` + `prasang.html` from `content/prasang/*.md` |
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

## Prasang ("तुम्ही काय कराल?" — apply the teaching)

Standalone situational-quiz pages, deliberately **separate from adhyay/concept** — a life scenario,
three response options, and a correct answer explained through specific Gita shlokas. A single
situation's explanation can cite (and link to) more than one sankalpana concept, since real
situations rarely map to just one teaching.

- Source: `content/prasang/*.md` — sections `## परिस्थिती` (situation), `## पर्याय` (options,
  lines starting `A.`/`B.`/`C.`), `## योग्य उत्तर` (correct letter), `## श्लोक` (shloka line +
  reference line), `## स्पष्टीकरण` (explanation, markdown `**bold**` supported), `## संबंधित
  संकल्पना` (comma-separated sankalpana slugs — resolved to titles at build time by reading each
  slug's `content/sankalpana/<slug>.md` H1, and rendered as linked pills to `sankalpana/<slug>.html`).
- Build: `python3 build_prasang.py` — add the new slug to `SLUGS` in that script first. Generates
  one `prasang/<slug>.html` per situation, `prasang/index.html` (redirect fallback for the bare
  directory URL, mirroring `sankalpana/index.html`), and `prasang.html` at the repo root (the real
  browsable listing page — this is what the nav's "प्रसंग" link points to).
  Loads `js/notify.js` + `js/sankalpana-list.js` like sankalpana pages, so the notification-settings
  menu entry appears there too.
- The interactive quiz card (`.ls-*` CSS classes, click-to-reveal JS) is inlined per generated page
  — no shared JS file, matching how sankalpana pages inline their own script blocks.
- Nav link ("प्रसंग", after "संकल्पना") is duplicated across `index.html`, `adhyay.html`,
  `about.html`, and the sankalpana template in `build_sankalpana.py` — same duplication pattern as
  the rest of the site's header/footer, so add it in all of those if the nav ever changes again.
- **Home page card** (`#prasang-home` in `index.html`, rendered by the last IIFE in `js/home.js`):
  picks one *random* (not day-indexed, unlike the "आजची संकल्पना" card) entry from
  `js/prasang-list.js` — an auto-generated full-data manifest (situation/correct/shloka/explanation
  HTML/related concepts, not just `{slug,title}` like `sankalpana-list.js`) — and renders the
  situation fully revealed (no click-to-answer interaction on the home page, unlike the standalone
  `prasang/*.html` pages), with a button to solve that exact situation and a button to the listing
  page. `js/prasang-list.js` is loaded **synchronously** right before `js/home.js` (not `defer`,
  unlike `sankalpana-list.js`) — home.js's IIFEs run inline at that script tag, before deferred
  head scripts fire, so a deferred prasang-list.js would still be `undefined` when home.js reads it.
  There's also a plain "प्रसंग पाहा" pill next to "संकल्पना पाहा" in the hero, linking to `./prasang`.

---

## Daily Sankalpana Notifications

`js/notify.js` — client-side-only notification engine (no push server; works inside the Android
TWA the same as in a browser, since a TWA is just Chrome rendering the PWA). Loaded via
`<script src="js/notify.js" defer>` on `index.html`, `adhyay.html`, `about.html`, and every
`sankalpana/*.html` page.

- Injects a "🔔 दैनंदिन सूचना" entry into every page's `#mobile-nav .wrap` and opens a settings
  modal (inline-styled, no new CSS) with an enable toggle + `<input type="time">`.
- Settings persist to `localStorage['gita-notify-settings']` as `{enabled, hour, minute}`.
  `Notification.requestPermission()` is only called from that modal's Save click (user gesture).
- Rotation: epoch-day index (`START_DATE = 2026-04-20`, same epoch as the daily email) modulo
  `window.SANKALPANA_LIST.length` — a separate rotation from `js/home.js`'s day-of-year concept
  picker and from `scripts/send_daily_concept.py`'s email index. All three are intentionally
  independent.
- Checked on `DOMContentLoaded`, `visibilitychange`, and a 60s `setInterval` — i.e. only while the
  app is open/foregrounded. If the app stays fully closed past the configured time, the
  notification fires next time it's opened, not at the exact clock time.
- `js/sankalpana-list.js` (the `{slug, title}` rotation source) is auto-generated by
  `build_sankalpana.py`'s `main()` — never hand-edit it, re-run the build script instead.
- `sw.js` has a `notificationclick` listener that focuses/opens the linked sankalpana page.

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
- **SW cache change**: Bump the `CACHE` version (e.g. `gita-v40` → `gita-v41`) in `sw.js`.
- **New sankalpana concept**: Add markdown to `content/sankalpana/`, add slug to `SLUGS` list in `build_sankalpana.py`, run the build script.
- **New प्रसंग situation**: Add markdown to `content/prasang/`, add slug to `SLUGS` list in `build_prasang.py`, run `python3 build_prasang.py` (regenerates `prasang/*.html`, `prasang/index.html`, and the root `prasang.html` listing).
- **OG shim pages**: Run `scripts/generate_adhyay_shims.py` or `generate_missing_shims.py` after adding new concepts.

---

## Local Dev

```sh
python3 serve.py   # or ./serve.sh
```

Opens a local server. GitHub Pages serves the site from the `main` branch root.
