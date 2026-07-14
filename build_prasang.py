#!/usr/bin/env python3
"""
build_prasang.py — Build all "प्रसंग" (life-situation) HTML pages from
content/prasang/*.md. A प्रसंग is a standalone situation/quiz page: one
scenario, three response options, a correct answer explained through Gita
shlokas, and links out to the sankalpana concept(s) it draws on — a single
situation may point at more than one concept.

Run from project root: python3 build_prasang.py
"""
import re, json
from pathlib import Path

SOURCE_DIR = Path("content/prasang")
OUTPUT_DIR = Path("prasang")
SANKALPANA_SOURCE_DIR = Path("content/sankalpana")

SLUGS = [
    "shreya-krodh",
    "tulana-irsha",
    "dirghasutri",
    "apayash-parishram",
    "khote-bolane",
    "sopa-durlabh-paisa",
    "bhashan-bhiti",
    "seva-thakwa",
    "hav-tulana",
    "mitra-durawa",
    "naukri-asurakshitata",
    "screen-vyasan",
    "palak-nirnay-vaad",
    "nivrutti-nirthakta",
    "padoutti-nakarli",
    "online-tika",
    "arogya-bhiti",
    "manasik-vishwasghat-mohh",
    "vyavasay-apayash-karj",
    "kishoravastha-bandkhori",
    "anolakhi-madat",
    "achanak-dhan-prapti",
]


def parse_inline(text):
    """Convert basic markdown inline to HTML: **bold**, *italic*, `code`."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def paragraphs_html(text, cls="ls-explain"):
    paras = [p.strip() for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]
    return '\n'.join(
        f'      <p class="{cls}">{parse_inline(" ".join(p.split()))}</p>'
        for p in paras
    )


def sankalpana_title(slug):
    p = SANKALPANA_SOURCE_DIR / f"{slug}.md"
    if not p.exists():
        return slug
    m = re.search(r'^# (.+)', p.read_text(encoding='utf-8'), re.MULTILINE)
    return m.group(1).strip() if m else slug


def parse_file(path):
    text = path.read_text(encoding='utf-8')
    data = {}

    m = re.search(r'^# (.+)', text, re.MULTILINE)
    data['title'] = m.group(1).strip() if m else path.stem

    parts = re.split(r'\n## ', '\n' + text)
    sections = {}
    for part in parts[1:]:
        lines = part.strip().split('\n')
        header = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        sections[header] = body

    data['situation'] = sections.get('परिस्थिती', '').strip()

    opt_text = sections.get('पर्याय', '')
    opt_matches = re.findall(r'^([ABC])\.\s*(.+?)(?=\n[ABC]\.|\Z)', opt_text, re.DOTALL | re.MULTILINE)
    data['options'] = [
        {'letter': letter, 'text': ' '.join(body.split())}
        for letter, body in opt_matches
    ]

    data['correct'] = sections.get('योग्य उत्तर', '').strip()[:1].upper()

    shloka_lines = [l.strip() for l in sections.get('श्लोक', '').strip().split('\n') if l.strip()]
    data['shloka'] = shloka_lines[0] if shloka_lines else ''
    data['shloka_ref'] = shloka_lines[1] if len(shloka_lines) > 1 else ''

    data['explanation'] = sections.get('स्पष्टीकरण', '').strip()

    related_raw = sections.get('संबंधित संकल्पना', '').strip()
    data['related'] = [s.strip() for s in related_raw.split(',') if s.strip()]

    return data


def situation_teaser(situation, length=110):
    flat = ' '.join(situation.split())
    return flat if len(flat) <= length else flat[:length].rsplit(' ', 1)[0] + '…'


def generate_html(data, slug):
    options_html = '\n'.join(
        f'''      <button class="ls-opt" data-opt="{o['letter'].lower()}">
        <span class="ls-opt-label">{o['letter']}</span>
        <span>{parse_inline(o['text'])}</span>
      </button>'''
        for o in data['options']
    )

    correct_letter = data['correct']
    correct_lower = correct_letter.lower()
    explanation_html = paragraphs_html(data['explanation'])

    related_html = '\n'.join(
        f'        <a class="pr-tag" href="../sankalpana/{s}.html">{sankalpana_title(s)}</a>'
        for s in data['related']
    )

    title = data['title']

    return f'''<!doctype html>
<html lang="mr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} — प्रसंग · गीता-ज्ञानेश्वरी</title>
<meta name="theme-color" content="#9c4a10" />
<link rel="icon" type="image/png" sizes="192x192" href="../assets/icons/icon-192.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="../css/style.css" />
<script src="../js/share.js" defer></script>
<script src="../js/pwa-update.js" defer></script>
<script src="../js/sankalpana-list.js" defer></script>
<script src="../js/notify.js" defer></script>
<style>
{PRASANG_STYLE_BLOCK}
</style>
</head>
<body>

<!-- NAV -->
<header class="nav">
  <div class="wrap nav-inner">
    <a class="brand" href="../">
      <span class="brand-mark">ॐ</span>
      <span>गीता-ज्ञानेश्वरी</span>
    </a>
    <nav class="nav-links">
      <a href="../">होम</a>
      <a href="../adhyay">अध्याय</a>
      <a href="../concept">संकल्पना</a>
      <a href="../prasang" class="on">प्रसंग</a>
    </nav>
    <button class="menu-btn" id="menu-btn" aria-label="मेनू" aria-expanded="false">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
  <div class="mobile-nav" id="mobile-nav" aria-hidden="true">
    <div class="wrap">
      <a href="../">होम</a>
      <a href="../#chapters">अध्याय</a>
      <a href="../concept">संकल्पना</a>
      <a href="../prasang" class="on">प्रसंग</a>
    </div>
  </div>
</header>

<section class="pr-hero">
  <div class="wrap-narrow">
    <div class="crumb">
      <a href="../">होम</a>
      <span class="sep">/</span>
      <a href="../prasang">प्रसंग</a>
      <span class="sep">/</span>
      <span class="now">{title}</span>
    </div>

    <div class="ls-card" id="ls-card">
      <div class="ls-eyebrow">🧭 प्रसंग — जगात आणा</div>
      <h1 class="pr-title">{title}</h1>

      <p class="ls-situation">{parse_inline(data['situation'])}</p>

      <p class="ls-question">तुम्ही काय कराल?</p>

      <div class="ls-options" id="ls-options">
{options_html}
      </div>

      <div class="ls-result" id="ls-result">
        <span class="ls-result-tag">योग्य उत्तर — {correct_letter}</span>
        <p class="ls-shloka">"{data['shloka']}"</p>
        <p class="ls-shloka-ref">— {data['shloka_ref']}</p>
{explanation_html}
        <div class="pr-related">
          <span class="pr-related-label">संबंधित संकल्पना:</span>
{related_html}
        </div>
        <button class="ls-retry" id="ls-retry">↺ पुन्हा प्रयत्न करा</button>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="../" style="font-size:22px;">
          <span class="brand-mark" style="width:34px;height:34px;font-size:18px;">ॐ</span>
          <span>गीता-ज्ञानेश्वरी</span>
        </a>
        <p class="foot-blurb">गीता आणि ज्ञानेश्वरी — आधुनिक जीवनासाठी एका शांत वाचनाच्या स्वरूपात.</p>
      </div>
      <div>
        <h5>ग्रंथ</h5>
        <a href="../#chapters">सर्व अध्याय</a>
        <a href="../concept">संकल्पना</a>
        <a href="../prasang">प्रसंग</a>
      </div>
      <div>
        <h5>बद्दल</h5>
        <a href="../about">या प्रकल्पाबद्दल</a>
        <a href="../privacy">गोपनीयता धोरण</a>
      </div>
    </div>
    <div class="foot-bottom">
      <div>© २०२६ गीता-ज्ञानेश्वरी · प्रेमाने बनवलेले.</div>
      <div class="right">"योगः कर्मसु कौशलम्" — गीता २.५०</div>
    </div>
  </div>
</footer>

<script>
  (function () {{
    var CORRECT = '{correct_lower}';
    var optionsEl = document.getElementById('ls-options');
    var resultEl = document.getElementById('ls-result');
    var retryBtn = document.getElementById('ls-retry');

    function reveal(selected) {{
      var opts = optionsEl.querySelectorAll('.ls-opt');
      opts.forEach(function (btn) {{
        btn.disabled = true;
        var opt = btn.getAttribute('data-opt');
        if (opt === CORRECT) {{
          btn.classList.add('correct');
        }} else if (opt === selected) {{
          btn.classList.add('wrong');
        }} else {{
          btn.classList.add('dim');
        }}
      }});
      resultEl.classList.add('show');
      resultEl.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }}

    optionsEl.addEventListener('click', function (e) {{
      var btn = e.target.closest('.ls-opt');
      if (!btn || btn.disabled) return;
      reveal(btn.getAttribute('data-opt'));
    }});

    retryBtn.addEventListener('click', function () {{
      var opts = optionsEl.querySelectorAll('.ls-opt');
      opts.forEach(function (btn) {{
        btn.disabled = false;
        btn.classList.remove('correct', 'wrong', 'dim');
      }});
      resultEl.classList.remove('show');
    }});
  }})();
</script>
<script>
  const menuBtn = document.getElementById('menu-btn');
  const nav = menuBtn && menuBtn.closest('.nav');
  if (menuBtn && nav) {{
    menuBtn.addEventListener('click', () => {{
      const open = nav.classList.toggle('menu-open');
      menuBtn.setAttribute('aria-expanded', open);
    }});
    document.addEventListener('click', e => {{
      if (nav.classList.contains('menu-open') && !nav.contains(e.target)) {{
        nav.classList.remove('menu-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }}
    }});
  }}
</script>

</body>
</html>'''


PRASANG_STYLE_BLOCK = '''
  body { background: var(--bg); }
  .pr-hero { padding: 28px 0 64px; }
  .pr-title {
    font-family: var(--serif-dev); font-size: clamp(28px, 4vw, 38px);
    color: var(--ink); margin: 18px 0 22px;
  }

  .ls-card {
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: 16px;
    box-shadow: var(--shadow-lg);
    padding: 28px 26px 30px;
    font-family: var(--sans-dev);
  }
  .ls-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 12.5px; font-weight: 700; letter-spacing: 0.06em;
    color: var(--saffron-deep); text-transform: uppercase;
  }
  .ls-situation {
    font-family: var(--serif-dev);
    font-size: 19px; line-height: 1.65;
    color: var(--ink); margin: 0 0 22px;
  }
  .ls-question {
    font-family: var(--sans-dev); font-weight: 700; font-size: 15px;
    color: var(--ink-soft); margin: 0 0 14px;
  }
  .ls-options { display: flex; flex-direction: column; gap: 10px; }
  .ls-opt {
    display: flex; align-items: flex-start; gap: 12px;
    width: 100%; text-align: left;
    background: var(--surface-2);
    border: 1.5px solid var(--rule);
    border-radius: 12px;
    padding: 14px 16px;
    font-family: var(--sans-dev); font-size: 15px; line-height: 1.5;
    color: var(--ink); cursor: pointer;
    transition: border-color var(--transition), background var(--transition), transform var(--transition);
  }
  .ls-opt:hover:not(:disabled) { border-color: var(--saffron); transform: translateY(-1px); }
  .ls-opt-label {
    flex-shrink: 0; width: 26px; height: 26px; border-radius: 50%;
    background: var(--rule-soft); color: var(--ink-soft);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 13px;
  }
  .ls-opt:disabled { cursor: default; }
  .ls-opt.correct {
    border-color: var(--leaf); background: color-mix(in oklab, var(--leaf) 12%, var(--surface-2));
  }
  .ls-opt.correct .ls-opt-label { background: var(--leaf); color: #fff; }
  .ls-opt.wrong {
    border-color: #b3453a; background: color-mix(in oklab, #b3453a 10%, var(--surface-2));
    opacity: 0.85;
  }
  .ls-opt.wrong .ls-opt-label { background: #b3453a; color: #fff; }
  .ls-opt.dim { opacity: 0.55; }

  .ls-result {
    margin-top: 22px; padding-top: 20px;
    border-top: 1px solid var(--rule);
    display: none;
    animation: lsFadeIn 0.4s ease;
  }
  .ls-result.show { display: block; }
  @keyframes lsFadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  .ls-result-tag {
    display: inline-block; font-size: 12.5px; font-weight: 700;
    letter-spacing: 0.04em; color: #fff; background: var(--leaf);
    border-radius: 999px; padding: 4px 12px; margin-bottom: 12px;
  }
  .ls-shloka {
    font-family: var(--serif-dev); font-style: italic;
    font-size: 17px; line-height: 1.7; color: var(--saffron-deep);
    margin: 0 0 6px;
  }
  .ls-shloka-ref {
    font-family: var(--sans-dev); font-size: 12.5px; color: var(--ink-mute);
    margin: 0 0 16px;
  }
  .ls-explain {
    font-family: var(--sans-dev); font-size: 15px; line-height: 1.75;
    color: var(--ink-soft); margin: 0 0 12px;
  }
  .ls-explain strong { color: var(--ink); }
  .pr-related {
    margin-top: 18px; display: flex; align-items: center; flex-wrap: wrap; gap: 8px;
  }
  .pr-related-label {
    font-family: var(--sans-dev); font-size: 13px; font-weight: 600; color: var(--ink-mute);
  }
  .pr-tag {
    font-family: var(--sans-dev); font-size: 13px; font-weight: 600;
    color: var(--saffron-deep); background: var(--primary-lt);
    border-radius: 999px; padding: 5px 14px; text-decoration: none;
  }
  .pr-tag:hover { background: var(--saffron-glow); color: #fff; }
  .ls-retry {
    margin-top: 20px; display: inline-flex; align-items: center; gap: 6px;
    background: none; border: 1px solid var(--rule); border-radius: 999px;
    padding: 8px 18px; font-family: var(--sans-dev); font-size: 13.5px;
    font-weight: 600; color: var(--ink-soft); cursor: pointer;
  }
  .ls-retry:hover { border-color: var(--saffron-deep); color: var(--saffron-deep); }
'''


def generate_listing_html(items):
    """prasang/index.html — the real browsable listing page, linked from the main nav
    as `./prasang` (root pages) / `../prasang` (subpages). NOTE: this lives INSIDE the
    prasang/ directory (not a sibling prasang.html at repo root) because a static file
    server resolves a bare `/prasang` URL to the prasang/ directory's own index first —
    a sibling `prasang.html` at root would be unreachable via that link."""
    cards = '\n'.join(
        f'''      <a class="pr-card" href="{it['slug']}.html">
        <span class="pr-card-eyebrow">🧭 प्रसंग</span>
        <h3>{it['title']}</h3>
        <p>{situation_teaser(it['situation'])}</p>
        <span class="pr-card-cta">विचार करा →</span>
      </a>'''
        for it in items
    )

    return f'''<!doctype html>
<html lang="mr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>प्रसंग · गीता-ज्ञानेश्वरी</title>
<meta name="theme-color" content="#9c4a10" />
<link rel="icon" type="image/png" sizes="192x192" href="../assets/icons/icon-192.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="../css/style.css" />
<script src="../js/share.js" defer></script>
<script src="../js/pwa-update.js" defer></script>
<script src="../js/sankalpana-list.js" defer></script>
<script src="../js/notify.js" defer></script>
<style>
  body {{ background: var(--bg); }}
  .pr-list-hero {{ padding: 48px 0 12px; }}
  .pr-list-hero h1 {{ font-family: var(--serif-dev); font-size: clamp(30px, 4.5vw, 44px); color: var(--ink); margin: 0 0 12px; }}
  .pr-list-hero p {{ font-family: var(--sans-dev); font-size: 16px; color: var(--ink-soft); max-width: 620px; line-height: 1.6; margin: 0; }}
  .pr-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; padding: 32px 0 64px; }}
  .pr-card {{
    display: flex; flex-direction: column; gap: 8px;
    background: var(--surface); border: 1px solid var(--rule); border-radius: 14px;
    padding: 22px 20px; text-decoration: none; box-shadow: var(--shadow-sm);
    transition: box-shadow var(--transition), transform var(--transition);
  }}
  .pr-card:hover {{ box-shadow: var(--shadow-md); transform: translateY(-2px); }}
  .pr-card-eyebrow {{ font-family: var(--sans-dev); font-size: 12px; font-weight: 700; letter-spacing: 0.05em; color: var(--saffron-deep); text-transform: uppercase; }}
  .pr-card h3 {{ font-family: var(--serif-dev); font-size: 20px; color: var(--ink); margin: 0; }}
  .pr-card p {{ font-family: var(--sans-dev); font-size: 14px; color: var(--ink-soft); line-height: 1.55; margin: 0; }}
  .pr-card-cta {{ font-family: var(--sans-dev); font-size: 13.5px; font-weight: 700; color: var(--saffron-deep); margin-top: 6px; }}
</style>
</head>
<body>

<header class="nav">
  <div class="wrap nav-inner">
    <a class="brand" href="../">
      <span class="brand-mark">ॐ</span>
      <span>गीता-ज्ञानेश्वरी</span>
    </a>
    <nav class="nav-links">
      <a href="../">होम</a>
      <a href="../#chapters">अध्याय</a>
      <a href="../concept">संकल्पना</a>
      <a href="./" class="on">प्रसंग</a>
    </nav>
    <button class="menu-btn" id="menu-btn" aria-label="मेनू" aria-expanded="false">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
  <div class="mobile-nav" id="mobile-nav" aria-hidden="true">
    <div class="wrap">
      <a href="../">होम</a>
      <a href="../#chapters">अध्याय</a>
      <a href="../concept">संकल्पना</a>
      <a href="./" class="on">प्रसंग</a>
    </div>
  </div>
</header>

<section class="pr-list-hero">
  <div class="wrap-narrow">
    <h1>प्रसंग — जगात आणा.</h1>
    <p>रोजच्या जीवनातला एक प्रसंग, तीन पर्याय — तुम्ही काय कराल? निवडा, आणि गीता काय सांगते ते पाहा.</p>
  </div>
</section>

<section class="wrap-narrow">
  <div class="pr-grid">
{cards}
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="../" style="font-size:22px;">
          <span class="brand-mark" style="width:34px;height:34px;font-size:18px;">ॐ</span>
          <span>गीता-ज्ञानेश्वरी</span>
        </a>
        <p class="foot-blurb">गीता आणि ज्ञानेश्वरी — आधुनिक जीवनासाठी एका शांत वाचनाच्या स्वरूपात.</p>
      </div>
      <div>
        <h5>ग्रंथ</h5>
        <a href="../#chapters">सर्व अध्याय</a>
        <a href="../concept">संकल्पना</a>
        <a href="./">प्रसंग</a>
      </div>
      <div>
        <h5>बद्दल</h5>
        <a href="../about">या प्रकल्पाबद्दल</a>
        <a href="../privacy">गोपनीयता धोरण</a>
      </div>
    </div>
    <div class="foot-bottom">
      <div>© २०२६ गीता-ज्ञानेश्वरी · प्रेमाने बनवलेले.</div>
      <div class="right">"योगः कर्मसु कौशलम्" — गीता २.५०</div>
    </div>
  </div>
</footer>

<script>
  const menuBtn = document.getElementById('menu-btn');
  const nav = menuBtn && menuBtn.closest('.nav');
  if (menuBtn && nav) {{
    menuBtn.addEventListener('click', () => {{
      const open = nav.classList.toggle('menu-open');
      menuBtn.setAttribute('aria-expanded', open);
    }});
    document.addEventListener('click', e => {{
      if (nav.classList.contains('menu-open') && !nav.contains(e.target)) {{
        nav.classList.remove('menu-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }}
    }});
  }}
</script>

</body>
</html>'''


def generate_list_js(entries):
    """js/prasang-list.js — full-data manifest consumed by js/home.js for the
    random-situation card on the home page (situation, answer, explanation,
    related sankalpana links) — no need to re-fetch/parse HTML client-side."""
    def entry_js(e):
        data = e['data']
        explanation_paras = [
            parse_inline(' '.join(p.split()))
            for p in re.split(r'\n\s*\n', data['explanation'].strip()) if p.strip()
        ]
        related = [{'slug': s, 'title': sankalpana_title(s)} for s in data['related']]
        options = [{'letter': o['letter'], 'text': parse_inline(o['text'])} for o in data['options']]
        obj = {
            'slug': e['slug'],
            'title': data['title'],
            'situation': data['situation'],
            'options': options,
            'correct': data['correct'],
            'shloka': data['shloka'],
            'shlokaRef': data['shloka_ref'],
            'explanation': explanation_paras,
            'related': related,
        }
        return json.dumps(obj, ensure_ascii=False, indent=2)

    items_js = ',\n'.join(entry_js(e) for e in entries)
    return (
        "// Auto-generated by build_prasang.py — do not edit by hand.\n"
        "window.PRASANG_LIST = [\n" + items_js + "\n];\n"
    )


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    generated = []
    for slug in SLUGS:
        p = SOURCE_DIR / f"{slug}.md"
        if not p.exists():
            print(f"  SKIP {slug} (file not found)")
            continue
        data = parse_file(p)
        html = generate_html(data, slug)
        out_path = OUTPUT_DIR / f"{slug}.html"
        out_path.write_text(html, encoding='utf-8')
        generated.append({'slug': slug, 'title': data['title'], 'situation': data['situation'], 'data': data})
        print(f"  ✓ prasang/{slug}.html  ({data['title']})")

    (OUTPUT_DIR / 'index.html').write_text(generate_listing_html(generated), encoding='utf-8')
    print(f"\nWrote prasang/index.html (listing page, {len(generated)} entries)")

    list_js_path = Path('js/prasang-list.js')
    list_js_path.write_text(generate_list_js(generated), encoding='utf-8')
    print(f"Wrote {list_js_path} ({len(generated)} entries)")

    print(f"\nDone — {len(generated)} प्रसंग pages in {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
