# गीता-ज्ञानेश्वरी — Project Context Document

> Use this document to brief Claude (Teams account) about this project. It covers the purpose, architecture, all key files, data structures, and ongoing conventions.

---

## 1. What This Project Is

**गीता-ज्ञानेश्वरी — आधुनिक जीवनदर्शन** is a Marathi Progressive Web App (PWA) that presents the Bhagavad Gita's 18 chapters (अध्याय) through the lens of modern everyday life. Each chapter contains multiple concepts (संकल्पना), and each concept is brought to life through:

- A **concept infographic image** (`.jpg`)
- A **PDF** with visual explanation
- **Trigger text** (hook paragraphs that draw the reader in)
- A **story** (कथा) — either a structured JS object or a standalone HTML page — showing how the concept applies to modern Marathi life
- A **Dnyaneshwari commentary** section (ज्ञानेश्वर महाराज काय म्हणतात)
- An optional **audio** (श्रवण) clip

The app is deployed on **GitHub Pages** at:  
`https://vivek-sovani.github.io/BhagvadgitaMarathi/`

---

## 2. Project Structure

```
BhagvadgitaMarathi/
├── index.html                  # Home page — chapter grid
├── adhyay.html                 # Chapter/concept viewer (SPA)
├── concept.html                # (older concept page, mostly replaced by adhyay.html)
├── about.html / privacy.html
├── manifest.json               # PWA manifest
├── sw.js                       # Service worker (cache version: gita-v27)
├── _config.yml                 # Jekyll config (for GitHub Pages)
│
├── js/
│   ├── data.js                 # GITA_DATA — all 18 chapter/concept metadata
│   ├── content.js              # GITA_CONTENT — text content per concept (large file)
│   ├── stories.js              # GITA_STORIES — structured story data per concept
│   ├── triggers.js             # GITA_TRIGGERS — hook/teaser text per concept
│   ├── adhyay.js               # Main SPA controller for adhyay.html
│   ├── home.js                 # Home page — chapter grid + daily concept picker
│   ├── share.js                # Share button (WhatsApp + clipboard)
│   ├── pdf-carousel.js         # PDF carousel component
│   ├── pwa-update.js           # Detects SW updates, shows "update available" banner
│   └── pdf.worker.min.js       # pdf.js worker
│
├── css/
│   └── style.css               # All styles (single file)
│
├── assets/
│   ├── adhyay-1/ … adhyay-18/  # Per-chapter assets
│   │   ├── adhyay.pdf          # Full chapter visual PDF
│   │   ├── summary.jpg         # Chapter summary image
│   │   ├── concept-1.jpg … concept-N.jpg    # Per-concept infographic images
│   │   ├── concept-1.pdf … concept-N.pdf    # Per-concept PDF
│   │   ├── concept-N-katha.pdf              # Katha (story) PDF (optional)
│   │   ├── concept-N-shravan.m4a            # Audio clip (optional)
│   │   └── README.txt          # Asset status notes for the chapter
│   ├── home-banner-landscape.jpg / home-banner-potrait.jpg
│   └── icons/                  # PWA icons (192, 512, maskable)
│
├── sankalpana/                 # Standalone Sankalpana concept pages (70+ HTML files)
│   ├── index.html              # Sankalpana listing page
│   └── *.html                  # One HTML per concept (e.g. sthitapradnya.html)
│
├── c/                          # OG-preview shim pages (redirect + meta tags)
│   └── {adhyayId}/{conceptId}/ # e.g. c/1/1/ → sets og:image, redirects to adhyay?id=1&concept=1
│
├── content/sankalpana/         # Source markdown for sankalpana pages
│   └── *.md                    # Markdown source (built by build_sankalpana.py)
│
├── scripts/
│   ├── send_daily_concept.py   # Daily email sender (run by GitHub Actions)
│   ├── generate_adhyay_shims.py
│   ├── generate_missing_shims.py
│   ├── insert_share_buttons.py
│   └── remove_notebooklm_watermark.py
│
├── adhyay1-whatsapp-links.md … adhyay13-whatsapp-links.md
│   # WhatsApp post text blocks — one per concept, separated by ━━━
│
├── build_sankalpana.py         # Build script: content/sankalpana/*.md → sankalpana/*.html
├── generate_og.py              # Generate OG image shim pages
├── compress_assets.py          # Compress images
├── compress_og.py
├── bump_og_version.py
├── serve.py / serve.sh         # Local dev server
│
└── .github/workflows/
    └── daily-concept-email.yml # GitHub Actions: sends daily email at 4:45 AM IST
```

---

## 3. Core Data Files

### `js/data.js` — GITA_DATA

The single source of truth for all 18 chapters and their concepts.

```js
const GITA_DATA = {
  adhyays: [
    {
      id: 1,
      number: "१",         // Devanagari numeral
      name: "अर्जुनविषादयोग",
      emoji: "😔",
      available: true,      // false = chapter not yet published
      summary: "...",       // Marathi summary shown on chapter cover page
      concepts: [
        {
          id: 1,
          emoji: "🏹",
          name: "धर्मक्षेत्रे कुरुक्षेत्रे — ...",
          tagline: "..."    // short hook (used on home page daily concept card)
        },
        // ...
      ]
    },
    // ... all 18 adhyays
  ]
};
```

All 18 chapters are `available: true`. Adhyay 1 has 7 concepts, adhyay 2 has 7, adhyay 3 has 12, up to adhyay 18 with 10. Total ~140+ concepts across all chapters.

### `js/triggers.js` — GITA_TRIGGERS

Hook text shown on the section menu landing page before the user picks a section.

```js
const GITA_TRIGGERS = {
  [adhyayId]: {
    "[conceptId]": {
      paras: ["para 1 HTML", "para 2 HTML", ...],
      cta:   "closing call-to-action line"
    }
  }
};
```

Currently covers adhyays 1–13 (all published adhyays). Inline HTML (`<strong>`, `<em>`) is allowed in `paras`.

### `js/stories.js` — GITA_STORIES

Story/katha content for the कथा section.

```js
const GITA_STORIES = {
  [adhyayId]: {
    "[conceptId]": {
      // Option A — external HTML page (adhyay 8–18, "combined" adhyays)
      kathaHtmlUrl: "assets/adhyay-8/concept-3-katha.html",

      // Option B — structured data (adhyay 1–7)
      shloka: { ref: "गीता १.१", text: "...\n...", meaning: "..." },
      conceptSummary: "...",
      audioUrl: "assets/adhyay-2/concept-2-shravan.m4a",   // optional
      imageUrl: "...",    // optional — shown as first carousel slide
      pdfUrl:   "...",    // optional — katha PDF
      story: {
        scene: { emoji, title, subtitle },
        characters: [{ emoji, role, desc }],
        body: [
          { type: "para", text: "..." },
          { type: "dialogue", speaker: "...", text: "..." },
          { type: "inner-thought", speaker, text },
          { type: "hbox", variant: "gold"|"blue", label, text },
          { type: "contrast", items: [{ side, icon, label, text }] },
          { type: "diary", label, text },
          { type: "layers", header, items: [{ num, title, gita, story }] },
          { type: "grid", header, cols, items: [{ icon, label, shloka, text }] },
          { type: "traits", header, items: [{ emoji, text }] },
          { type: "vastra", header, left, right, footer }
        ],
        turningPoint: "...",
        gitaConnect: "...",
        reflection: "...",
        sankalp: "..."
      }
    }
  }
};
```

### `js/content.js` — GITA_CONTENT

Text content (vivechan / Dnyaneshwari commentary) per concept. Very large file (~845KB). Structure:

```js
const GITA_CONTENT = {
  "[adhyayId]": {
    "[conceptId]": "raw multiline text..."
  }
};
```

The raw text is parsed in `adhyay.js → renderConceptText()` using emoji markers:
- `📖` → श्लोक block
- `🟧` → ज्ञानेश्वरी block  
- `💡` → highlight / question
- `🌱` → संकल्प block
- Lines starting with certain emojis → header

---

## 4. Main SPA — `adhyay.js`

`adhyay.html?id=N` loads the chapter. `adhyay.html?id=N&concept=M` loads directly to a concept.

### Key Functions

| Function | What it does |
|---|---|
| `selectConcept(cid)` | Shows a concept — updates URL, renders image, text, story, PDF, section menu |
| `goToCoverPage()` | Returns to chapter cover (summary image + concept list) |
| `showSection(name)` | Shows one of: `'vivechan'`, `'katha'`, `'shravan'` |
| `showSectionMenu()` | Shows the section picker (3 cards) |
| `renderConceptText(adhyayId, conceptId)` | Parses GITA_CONTENT text → structured HTML |
| `renderStory(adhyayId, conceptId)` | Renders GITA_STORIES katha section |
| `renderPdfVertical(url)` | Renders PDF pages vertically in right panel using pdf.js |
| `renderStoryPdfPages(url, containerId, zoom, onDone, splitPages)` | Renders katha PDF as horizontal carousel slides |
| `attachPdfZoom(pagesEl)` | Adds pinch-to-zoom + Ctrl+scroll to a PDF carousel |
| `openStoryPdf(url, title)` | Opens story PDF in modal (desktop) or new tab (mobile) |
| `buildSectionNav(sectionId, hasStory)` | Builds cross-section pill navigation |

### Navigation Architecture

- **URL**: `adhyay?id=N` (cover), `adhyay?id=N&concept=M` (concept)
- **`history.pushState`** used throughout — back button navigates within the SPA
- **`popstate`** handler restores the correct view
- **Combined adhyays** (id 8–18): concept landing goes directly to `'katha'` section (which contains the merged vivechan + katha HTML), skipping the section menu

### isCombinedAdhyay

```js
const isCombinedAdhyay = (adhyayId >= 8 && adhyayId <= 18);
```

For combined adhyays, the `kathaHtmlUrl` in GITA_STORIES points to a standalone HTML file embedded in an `<iframe>`. The vivechan section card is hidden.

### Font Size

Persisted in `localStorage` under key `'gita-fontsize'`. Values: `'small'`, `'normal'`, `'large'`. Applied as `document.body.dataset.fontsize` and propagated into the katha iframe.

---

## 5. Home Page — `home.js`

Two responsibilities:

1. **Chapter grid**: Renders all 18 chapters from `GITA_DATA` with English subtitle and shloka count.
2. **Daily concept picker**: Picks one concept per day (same all day, rotates daily by day-of-year). Looks for concepts that have `GITA_TRIGGERS` data. Shows in two places:
   - `#sc-ref / #sc-shlok / #sc-ovi / #sc-meaning` (scroll card)
   - `#tv-ref / #tv-quote / #tv-cta` (today-verse section)

---

## 6. Sharing — `share.js`

Exposes `window.initShareButton(buttonEl, getShareData)`.
- On mobile (Web Share API available): uses native share sheet
- On desktop: opens a popover with WhatsApp link and Copy Link button

URLs for sharing use `/c/{adhyayId}/{conceptId}/` shim pages (which have proper OG meta tags for WhatsApp preview images). All 18 adhyays have shim pages.

---

## 7. Assets Per Chapter

Each `assets/adhyay-N/` folder contains:
- `adhyay.pdf` — full chapter visual PDF
- `summary.jpg` — chapter cover summary image
- `concept-M.jpg` — concept infographic
- `concept-M.pdf` — concept PDF (rendered in right panel carousel)
- `concept-M-katha.pdf` — story PDF (optional, shown in katha section)
- `concept-M-katha.html` — standalone katha HTML page (used for combined adhyays 8–18)
- `concept-M-shravan.m4a` — audio (optional, available for select adhyay 2 concepts)
- `README.txt` — manually maintained notes on what assets are ready

Image loading has a fallback chain: `.jpg → .jpeg → .png`.

---

## 8. Daily Email System

### WhatsApp Post Files (`adhyay1-whatsapp-links.md` … `adhyay13-whatsapp-links.md`)

Each file contains concept blocks separated by `━━━━━━━━━━━━━━━━━━━━━━━`. Each block has:
- `📅 दिवस N / संकल्पना M` header
- Bold chapter/concept title (`*...*`)
- A one-line italic summary (`_..._`)
- A link: `https://vivek-sovani.github.io/BhagvadgitaMarathi/c/{adhyayId}/{conceptId}/`

### `scripts/send_daily_concept.py`

- `START_DATE = date(2026, 4, 20)` — index 0 of the concept sequence
- Today's index = `(today - START_DATE).days % total_concepts`
- Loads `GITA_TRIGGERS` by running `js/triggers.js` via Node.js
- Builds an HTML email with: amber "आजचा विचार" box (trigger text) + WhatsApp post block
- Sends via Gmail SMTP (SSL, port 465) using `GMAIL_ADDRESS` + `GMAIL_APP_PASSWORD` env vars

**Current position (as of 2026-06-29)**: index 70 = adhyay 8, concept 3. Adhyay 8 concepts 1 & 2 were sent manually before the automation started.

### GitHub Actions (`.github/workflows/daily-concept-email.yml`)

Runs at `23:15 UTC` = `4:45 AM IST` every day. Secrets: `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`.

---

## 9. Sankalpana Section

`sankalpana/` contains 70+ standalone HTML pages — one per Gita concept/virtue (e.g. `sthitapradnya.html`, `samatva.html`). These are built from markdown sources in `content/sankalpana/*.md` using `build_sankalpana.py`.

`sankalpana/index.html` is the listing page. Each page has a share button auto-initialized by `window.autoInitSankalpanaShare()`.

---

## 10. PWA Setup

- **Service worker**: `sw.js` — Cache name `gita-v27`. Pre-caches all core JS/CSS/images. Uses cache-first strategy, network-fallback for HTML pages.
- **Manifest**: `manifest.json` — scope `/BhagvadgitaMarathi/`, lang `mr`, display `standalone`, theme `#9c4a10` (saffron-brown).
- **Update banner**: `pwa-update.js` listens for `controllerchange` event (new SW activated) and shows an "update available" banner.

---

## 11. URL Structure

| URL | What it shows |
|---|---|
| `/BhagvadgitaMarathi/` | Home — 18-chapter grid + daily concept |
| `/BhagvadgitaMarathi/adhyay?id=N` | Chapter N cover (summary + concept list) |
| `/BhagvadgitaMarathi/adhyay?id=N&concept=M` | Chapter N, Concept M |
| `/BhagvadgitaMarathi/c/N/` | OG shim for chapter N (redirects to adhyay?id=N) |
| `/BhagvadgitaMarathi/c/N/M/` | OG shim for chapter N concept M (has og:image) |
| `/BhagvadgitaMarathi/sankalpana/` | Sankalpana index |
| `/BhagvadgitaMarathi/sankalpana/{slug}.html` | Individual sankalpana concept |

---

## 12. Key Conventions

1. **Devanagari numerals** are used for display throughout. `toDevNum(n)` in `adhyay.js` converts `1` → `१`.
2. **`available: true/false`** in `GITA_DATA` controls whether a chapter is clickable.
3. **Adding a new chapter** means: adding to `GITA_DATA`, creating assets in `assets/adhyay-N/`, adding trigger data to `GITA_TRIGGERS`, optionally adding story data to `GITA_STORIES`, and creating a WhatsApp post file.
4. **Combined adhyays** (8–18) use `kathaHtmlUrl` in GITA_STORIES pointing to `concept-N-katha.html` — these are full standalone HTML files embedded in an iframe. They combine vivechan + katha in one page.
5. **Adhyays 1–7** use structured `story` objects in `GITA_STORIES.js` and have separate vivechan text in `content.js`.
6. **Adhyay 4** is special: the katha section is labeled "आधुनिक योगी" instead of "आयुष्यातील क्षण".
7. **OG shim pages** in `/c/N/M/` are used for all WhatsApp share links so WhatsApp shows a preview image.
8. **Service worker cache version** in `sw.js` (`gita-v27`) must be bumped whenever cached files change.

---

## 13. Python Utility Scripts

| Script | Purpose |
|---|---|
| `scripts/send_daily_concept.py` | Daily email sender |
| `scripts/generate_adhyay_shims.py` | Generate `/c/N/M/` OG shim HTML files |
| `scripts/generate_missing_shims.py` | Generate any missing shims |
| `scripts/insert_share_buttons.py` | Batch-insert share buttons into HTML files |
| `scripts/remove_notebooklm_watermark.py` | Remove NotebookLM watermark from audio files |
| `build_sankalpana.py` | Build sankalpana HTML from markdown sources |
| `generate_og.py` | Generate OG images |
| `compress_assets.py` / `compress_og.py` | Compress images |
| `bump_og_version.py` | Bump OG cache-bust version |
| `serve.py` / `serve.sh` | Local dev server |

---

## 14. Current State (as of 2026-06-29)

- All 18 adhyays published (`available: true`)
- Email sequence running — at adhyay 8 concept 3 (index 70)
- WhatsApp post files exist for adhyays 1–13 (the email sequence covers adhyays 1–13)
- Adhyays 14–18 have infographic + presentation assets but no WhatsApp post files yet
- `adhyay 3 sample.html` is an uncommitted experimental file in the working directory
- `.claude/launch.json` has a minor modification (uncommitted)

---

*Generated from live code reading on 2026-06-29 for migration to Claude Teams account.*
