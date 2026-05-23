#!/usr/bin/env python3
"""
build_sankalpana.py — Build all sankalpana HTML pages from content/sankalpana/*.md
Run from project root: python3 build_sankalpana.py
"""
import os, re
from pathlib import Path

DEV_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

def dev_to_int(s):
    """Convert Devanagari numeral string to int (e.g. '१२' → 12)."""
    return int(s.translate(DEV_DIGITS))

SOURCE_DIR = Path("content/sankalpana")
OUTPUT_DIR = Path("sankalpana")

SLUGS = [
    "atmaswarup", "avyakta-vyakta", "bhaktiyog", "daivi-asuri-sampada",
    "dnyanyog", "gunatita", "karmarpan", "kshetra-kshetradnya",
    "lokasangraha", "maya", "moksha", "nishkam-karmayog",
    "prakriti-purusha", "samatva", "sannyasa-tyaga", "shraddha",
    "sthitapradnya", "trigunas", "vairagya", "vishwarupa",
    # new batch
    "abhaya", "ahimsa", "anasakthi", "astikya-buddhi", "chittashuddhi",
    "dhairya", "indriya-nigraha", "krutagnyata", "kshama", "kshanbhanguratha",
    "namasmarana", "prarabdha-purushartha", "samarpana", "sankalpa-vikalpa",
    "satsang", "satya", "sevabhava", "sharanagati", "svadharma",
    "tapa", "viveka", "yogakshema",
    # batch 3
    "chidananda", "ahaituki-krupa", "kshanti", "avyabhicharini-bhakti",
    "vivekhyati",
    # batch 4
    "buddhiyoga", "prasannachitta", "yoganishtha",
    # batch 5
    "divyabhava", "atmasakshi", "paramaprem", "chittaikagrata", "anugraha",
]

ICONS = [
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 9h18"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 19h16M6 19V9l6-4 6 4v10"/><path d="M10 19v-6h4v6"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 11c0 5.5-7 10-7 10z"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 2v6M5 12H2M22 12h-3M5.2 5.2l2.1 2.1M16.7 7.3l2.1-2.1"/><circle cx="12" cy="15" r="6"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>',
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3L2 9l10 6 10-6-10-6z"/><path d="M2 17l10 6 10-6"/><path d="M2 13l10 6 10-6"/></svg>',
]


def extract_code_blocks(text):
    """Return list of code block contents (stripped of ```)."""
    blocks = re.findall(r'```[^\n]*\n(.*?)```', text, re.DOTALL)
    return [b.strip() for b in blocks]


def strip_code_blocks(text):
    return re.sub(r'```[^\n]*\n.*?```', '', text, flags=re.DOTALL).strip()


def parse_inline(text):
    """Convert basic markdown inline to HTML: **bold**, *italic*, `code`."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def paragraphs_html(text, cls="body"):
    """Convert text into <p class=cls> paragraphs, skipping empty lines and blockquotes."""
    lines = text.strip().split('\n')
    paras = []
    buf = []
    for line in lines:
        line = line.strip()
        if not line:
            if buf:
                paras.append(' '.join(buf))
                buf = []
        elif line.startswith('> ') or line == '>':
            if buf:
                paras.append(' '.join(buf))
                buf = []
            # blockquotes shown as styled paragraph
            content = line[2:].strip()
            if content:
                paras.append(f'__BLOCKQUOTE__{content}')
        elif line.startswith('- ') or line.startswith('* '):
            if buf:
                paras.append(' '.join(buf))
                buf = []
            paras.append(f'__LISTITEM__{line[2:]}')
        elif re.match(r'^\d+\. ', line):
            if buf:
                paras.append(' '.join(buf))
                buf = []
            cleaned = re.sub(r'^\d+\. ', '', line)
            paras.append(f'__LISTITEM__{cleaned}')
        elif line.startswith('#'):
            pass  # skip sub-headings inside body
        else:
            buf.append(line)
    if buf:
        paras.append(' '.join(buf))

    html_parts = []
    list_open = False
    for p in paras:
        if p.startswith('__LISTITEM__'):
            if not list_open:
                html_parts.append('<ul style="margin:0 0 16px 20px;">')
                list_open = True
            html_parts.append(f'<li style="font-family:var(--serif-dev);font-size:19px;line-height:1.7;color:var(--ink-soft);margin-bottom:6px;">{parse_inline(p[12:])}</li>')
        else:
            if list_open:
                html_parts.append('</ul>')
                list_open = False
            if p.startswith('__BLOCKQUOTE__'):
                content = parse_inline(p[14:])
                html_parts.append(f'<p class="{cls}" style="border-left:3px solid var(--saffron);padding-left:18px;font-style:italic;">{content}</p>')
            else:
                html_parts.append(f'<p class="{cls}">{parse_inline(p)}</p>')
    if list_open:
        html_parts.append('</ul>')
    return '\n'.join(html_parts)


def parse_md_table(text):
    """Parse a markdown table — only reads lines starting with '|', preserving empty cells."""
    table_lines = [l.strip() for l in text.split('\n')
                   if l.strip().startswith('|') and not re.match(r'^\|[-:| ]+\|$', l.strip())]
    if not table_lines:
        return [], []

    def split_row(line):
        cells = line.split('|')
        if cells and cells[0].strip() == '':
            cells = cells[1:]
        if cells and cells[-1].strip() == '':
            cells = cells[:-1]
        return [c.strip() for c in cells]

    headers = split_row(table_lines[0])
    rows = [split_row(l) for l in table_lines[1:]]
    ncols = len(headers)
    rows = [r[:ncols] + [''] * max(0, ncols - len(r)) for r in rows]
    return headers, rows


def parse_file(path):
    text = path.read_text(encoding='utf-8')
    data = {}

    # Title (H1)
    m = re.search(r'^# (.+)', text, re.MULTILINE)
    data['title'] = m.group(1).strip() if m else path.stem

    # Split into sections by ## headings
    parts = re.split(r'\n## ', '\n' + text)
    sections = {}
    for part in parts[1:]:
        lines = part.strip().split('\n')
        header = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        sections[header] = body

    # ── केंद्रीय संकल्पना ──
    kendra_body = sections.get('गीतेची केंद्रीय संकल्पना', '')
    # First line after heading: bold part — title definition
    first_line_m = re.match(r'\*\*(.+?)\*\*\s*[—–-]\s*(.+)', kendra_body.split('\n')[0].strip())
    if first_line_m:
        data['kendra_bold'] = first_line_m.group(1).strip()
        data['kendra_def'] = first_line_m.group(2).strip()
    else:
        data['kendra_bold'] = data['title']
        data['kendra_def'] = ''
    # Opening blockquote in kendra section
    bq_m = re.search(r'^> \*?"?(.+?)"?\*?$', kendra_body, re.MULTILINE)
    data['kendra_quote'] = bq_m.group(1).strip() if bq_m else ''
    # Full intro paragraphs
    data['kendra_body'] = kendra_body

    # ── केंद्रीय श्लोक ──
    shloka_key = next((k for k in sections if k.startswith('केंद्रीय श्लोक')), None)
    if shloka_key:
        sb = sections[shloka_key]
        codes = extract_code_blocks(sb)
        data['shloka_header'] = shloka_key.replace('केंद्रीय श्लोक · ', '').strip()
        # Extract adhyay number for linking (e.g. "अध्याय २, श्लोक ४७" → 2)
        chap_m = re.search(r'अध्याय\s+([०-९]+)', data['shloka_header'])
        data['adhyay_num'] = dev_to_int(chap_m.group(1)) if chap_m else None
        data['adhyay_dev'] = chap_m.group(1) if chap_m else None  # keep Devanagari for display
        data['shloka_sanskrit'] = codes[0] if len(codes) > 0 else ''
        data['shloka_ovi'] = codes[1] if len(codes) > 1 else ''
        # अर्थ paragraph
        arth_m = re.search(r'\*\*अर्थ\*\*\s*\n+(.*?)(?:\n---|\Z)', sb, re.DOTALL)
        if not arth_m:
            # Try after last code block
            no_code = strip_code_blocks(sb)
            arth_m2 = re.search(r'\*\*अर्थ\*\*\s*\n+([\s\S]+)', no_code)
            data['shloka_arth'] = arth_m2.group(1).strip() if arth_m2 else ''
        else:
            data['shloka_arth'] = arth_m.group(1).strip()
        # Ovi label from heading (e.g. "ज्ञानेश्वरी ओवी · अध्याय २")
        ovi_label_m = re.search(r'\*\*(ज्ञानेश्वरी ओवी[^*]*)\*\*', sb)
        data['ovi_label'] = ovi_label_m.group(1).strip() if ovi_label_m else 'ज्ञानेश्वरी ओवी'
        # Source line from shloka header
        data['shloka_source'] = data['shloka_header']
    else:
        data['shloka_header'] = ''
        data['shloka_sanskrit'] = ''
        data['shloka_ovi'] = ''
        data['shloka_arth'] = ''
        data['ovi_label'] = 'ज्ञानेश्वरी ओवी'
        data['shloka_source'] = ''
        data['adhyay_num'] = None
        data['adhyay_dev'] = None

    # ── संकल्पनेचा अर्थ ──
    arth_key = 'संकल्पनेचा अर्थ'
    data['arth_body'] = sections.get(arth_key, '')

    # ── Comparison table (vs / तुलना / multi-part) ──
    SKIP_FOR_COMPARE = ('गीतेची केंद्रीय संकल्पना', 'संकल्पनेचा अर्थ',
                        'ज्ञानेश्वरी विवेचन', 'आधुनिक प्रसंग',
                        'गैरसमज', 'सार', 'केंद्रीय श्लोक',
                        'पुढे वाचा', 'रोजच्या जीवनात')
    compare_key = next((k for k in sections if ' vs ' in k), None)
    if not compare_key:
        # Also match तुलना and any non-standard section whose body contains a table
        for k in sections:
            if any(k.startswith(s) for s in SKIP_FOR_COMPARE):
                continue
            h, r = parse_md_table(sections[k])
            if len(h) >= 2 and r:
                compare_key = k
                break
    if compare_key:
        cb = sections[compare_key]
        headers, rows = parse_md_table(cb)
        data['compare_headers'] = headers   # full list including empty label column
        data['compare_left_title'] = headers[1] if len(headers) > 1 else ''
        data['compare_right_title'] = headers[2] if len(headers) > 2 else ''
        data['compare_rows'] = rows
        data['compare_key'] = compare_key
    else:
        data['compare_key'] = None
        data['compare_headers'] = []

    # ── ज्ञानेश्वरी विवेचन ──
    vivechan_key = 'ज्ञानेश्वरी विवेचन'
    if vivechan_key in sections:
        vb = sections[vivechan_key]
        codes = extract_code_blocks(vb)
        data['vivechan_body'] = strip_code_blocks(vb)
        data['vivechan_ovi'] = codes[0] if codes else ''
        # Source label: ### heading before code block
        ovi_src_m = re.search(r'### (.+)', vb)
        data['vivechan_ovi_label'] = ovi_src_m.group(1).strip() if ovi_src_m else 'ज्ञानेश्वरी ओवी'
        # Italicised translation after code block
        trans_m = re.search(r'```\s*\n\n\*"?(.+?)"?\*', vb, re.DOTALL)
        if not trans_m:
            trans_m = re.search(r'```\s*\n+\*(.+?)\*', vb, re.DOTALL)
        data['vivechan_translation'] = trans_m.group(1).strip() if trans_m else ''
    else:
        data['vivechan_body'] = ''
        data['vivechan_ovi'] = ''
        data['vivechan_ovi_label'] = ''
        data['vivechan_translation'] = ''

    # ── आधुनिक प्रसंग ──
    prasang_key = 'आधुनिक प्रसंग'
    scenarios = []
    if prasang_key in sections:
        pb = sections[prasang_key]
        # Split by ### sub-headings (numbered scenarios); prepend \n so first ### is also caught
        sub_parts = re.split(r'\n### ', '\n' + pb)
        for sp in sub_parts[1:]:
            sp_lines = sp.strip().split('\n')
            title = re.sub(r'^\d+\.\s*', '', sp_lines[0]).strip()
            body = '\n'.join(sp_lines[1:])
            # परिस्थिती
            sit_m = re.search(r'\*\*परिस्थिती:\*\*\s*"?(.+?)"?\s*(?:\n|$)', body)
            situation = sit_m.group(1).strip() if sit_m else ''
            # दृष्टिकोन (label varies)
            drushti_m = re.search(r'\*\*[^*]*दृष्टिकोन:\*\*\s*(.+?)(?=\n---|\n\n###|\Z)', body, re.DOTALL)
            perspective = drushti_m.group(1).strip() if drushti_m else ''
            perspective = re.sub(r'\n+', ' ', perspective).strip()
            scenarios.append({'title': title, 'situation': situation, 'perspective': perspective})
    data['scenarios'] = scenarios

    # ── गैरसमज ──
    myth_key = 'गैरसमज'
    if myth_key in sections:
        mb = sections[myth_key]
        # Title from blockquote bold
        myth_title_m = re.search(r'> \*\*(.+?)\*\*', mb)
        data['myth_title'] = myth_title_m.group(1).strip() if myth_title_m else 'गैरसमज'
        # Body paragraphs (non-blockquote)
        data['myth_body'] = strip_code_blocks(mb)
    else:
        data['myth_title'] = ''
        data['myth_body'] = ''

    # ── रोजच्या जीवनात (practice steps) ──
    practice_key = next((k for k in sections if k.startswith('रोजच्या जीवनात')), None)
    steps = []
    if practice_key:
        prb = sections[practice_key]
        headers, rows = parse_md_table(prb)
        for row in rows:
            num = re.sub(r'\*\*', '', row[0]).strip() if len(row) > 0 else ''
            step_title = re.sub(r'\*\*', '', row[1]).strip() if len(row) > 1 else ''
            action = row[2].strip() if len(row) > 2 else ''
            steps.append({'num': num, 'title': step_title, 'action': parse_inline(action)})
    data['steps'] = steps

    # ── पुढे वाचा (related concepts) ──
    related_key = next((k for k in sections if k.startswith('पुढे वाचा')), None)
    related = []
    if related_key:
        rb = sections[related_key]
        # Prepend \n so first ### at start-of-body is also caught
        sub_parts = re.split(r'\n### ', '\n' + rb)
        for sp in sub_parts[1:]:
            sp_lines = [l.strip() for l in sp.strip().split('\n') if l.strip()]
            if not sp_lines:
                continue
            header = sp_lines[0]
            # "Name · Chapter ref" format
            if ' · ' in header:
                parts = header.split(' · ', 1)
                rel_name = parts[0].strip()
                rel_ref = parts[1].strip()
            else:
                rel_name = header
                rel_ref = ''
            rel_desc = sp_lines[1] if len(sp_lines) > 1 else ''
            related.append({'name': rel_name, 'ref': rel_ref, 'desc': rel_desc})
    data['related'] = related

    # ── सार ──
    saar_key = 'सार'
    if saar_key in sections:
        sb2 = sections[saar_key]
        # All blockquote lines
        bq_lines = [l.lstrip('>').strip() for l in sb2.split('\n') if l.strip().startswith('>')]
        # Sanskrit/italic lines (not bold **) form the quote; bold lines form the meaning
        quote_lines = [l for l in bq_lines if l and not l.startswith('**')]
        meaning_lines = [re.sub(r'\*\*', '', l).strip() for l in bq_lines if l.startswith('**')]
        data['saar_quote'] = ' '.join(quote_lines).strip()
        data['saar_meaning'] = meaning_lines[0] if meaning_lines else ''
    else:
        data['saar_quote'] = ''
        data['saar_meaning'] = ''

    return data


def build_catalog():
    catalog = {}  # Devanagari title → slug
    for slug in SLUGS:
        p = SOURCE_DIR / f"{slug}.md"
        if p.exists():
            m = re.search(r'^# (.+)', p.read_text(encoding='utf-8'), re.MULTILINE)
            if m:
                catalog[m.group(1).strip()] = slug
    return catalog


STYLE_BLOCK = """
  /* ─── Concept hero ─── */
  .c-hero {
    background:
      radial-gradient(ellipse at 80% 0%, color-mix(in oklab, var(--saffron) 18%, var(--bg)) 0%, var(--bg) 55%);
    padding: 48px 0 100px;
    border-bottom: 1px solid var(--rule);
    position: relative;
    overflow: hidden;
  }
  @media (max-width: 880px) { .c-hero { padding: 32px 0 64px; } }

  .c-hero-inner {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 80px;
    align-items: end;
    margin-top: 40px;
  }
  @media (max-width: 980px) {
    .c-hero-inner { grid-template-columns: 1fr; gap: 48px; align-items: start; }
  }

  .c-tag-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 14px 0 28px; }

  .c-title {
    font-family: var(--serif-dev);
    font-weight: 600;
    font-size: clamp(50px, 7vw, 96px);
    line-height: 1.0;
    letter-spacing: -0.015em;
    margin: 0 0 24px;
    color: var(--ink);
  }
  .c-title em { font-style: normal; color: var(--saffron-deep); }
  .c-sub {
    font-family: var(--serif);
    font-style: italic;
    font-size: 22px;
    color: var(--ink-mute);
    margin: 0 0 28px;
  }
  .c-summary {
    font-family: var(--serif-dev);
    font-size: clamp(19px, 1.5vw, 22px);
    line-height: 1.65;
    color: var(--ink-soft);
    max-width: 580px;
    margin: 0 0 32px;
  }

  .origin-card {
    background: var(--paper);
    border: 1px solid var(--rule);
    border-radius: 24px;
    padding: 36px 32px;
    position: relative;
    box-shadow: 0 20px 50px -30px rgba(31,24,18,.3);
  }
  .origin-card .corner {
    position: absolute; top: -14px; left: 32px;
    background: var(--saffron-deep); color: var(--paper);
    padding: 6px 14px; border-radius: 999px;
    font-family: var(--mono); font-size: 11px;
    letter-spacing: 0.18em; text-transform: uppercase;
  }
  .origin-card .head {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--ink-mute); margin: 14px 0 14px;
  }
  .origin-card .shloka {
    font-family: var(--serif-dev); font-weight: 500; font-size: 22px;
    line-height: 1.55; margin: 0 0 22px; color: var(--ink);
  }
  .origin-card .ovi {
    font-family: var(--serif-dev); font-style: italic; font-size: 17px;
    line-height: 1.55; color: var(--ink-soft);
    border-top: 1px solid var(--rule); padding-top: 18px; margin: 0 0 18px;
  }
  .origin-card .ovi-label {
    font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--saffron-deep); margin-bottom: 8px;
  }
  .origin-card .source {
    display: flex; align-items: center; gap: 8px;
    font-family: var(--mono); font-size: 11px; color: var(--ink-mute); letter-spacing: 0.06em;
  }
  .origin-card .source::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--saffron);
  }

  .c-mandala {
    position: absolute; top: -180px; right: -180px; width: 580px; height: 580px;
  }

  .c-body { padding: 80px 0; }
  @media (max-width: 880px) { .c-body { padding: 56px 0; } }

  .c-section { margin-bottom: 80px; }
  .c-section:last-child { margin-bottom: 0; }
  .c-section .section-head { margin-bottom: 36px; max-width: 760px; }
  .c-section h2 {
    font-family: var(--serif-dev); font-weight: 600;
    font-size: clamp(28px, 3vw, 40px); line-height: 1.18;
    letter-spacing: -0.005em; margin: 12px 0 14px; color: var(--ink);
  }
  .c-section p.body {
    font-family: var(--serif-dev); font-size: 19px; line-height: 1.7;
    color: var(--ink-soft); margin: 0 0 16px; max-width: 760px;
  }
  .c-section p.body strong { color: var(--ink); font-weight: 600; }

  .compare { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 32px; }
  @media (max-width: 720px) { .compare { grid-template-columns: 1fr; } }
  .compare-col { background: var(--paper); border: 1px solid var(--rule); border-radius: 20px; padding: 32px 28px; }
  .compare-col h5 {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--ink-mute); margin: 0 0 14px; font-weight: 500;
  }
  .compare-col .big {
    font-family: var(--serif-dev); font-weight: 600; font-size: 26px;
    margin: 0 0 14px; color: var(--ink); line-height: 1.25;
  }
  .compare-col p { font-family: var(--serif-dev); font-size: 17px; line-height: 1.6; color: var(--ink-soft); margin: 0; }
  .compare-col.dark { background: var(--ink); border-color: var(--ink); color: var(--bg); }
  .compare-col.dark h5 { color: var(--saffron-glow); }
  .compare-col.dark .big { color: var(--bg); }
  .compare-col.dark p { color: rgba(251,246,234,.75); }

  .scenarios {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 32px;
  }
  @media (max-width: 980px) { .scenarios { grid-template-columns: 1fr 1fr; } }
  @media (max-width: 600px) { .scenarios { grid-template-columns: 1fr; } }
  .scn {
    background: var(--paper); border: 1px solid var(--rule); border-radius: 18px;
    padding: 28px 26px; display: flex; flex-direction: column;
    transition: transform .2s ease, border-color .2s ease;
  }
  .scn:hover { transform: translateY(-3px); border-color: color-mix(in oklab, var(--saffron) 35%, var(--rule)); }
  .scn .ic {
    width: 44px; height: 44px; border-radius: 12px; background: var(--bg-2);
    display: grid; place-items: center; color: var(--saffron-deep); margin-bottom: 22px;
  }
  .scn h4 { font-family: var(--serif-dev); font-weight: 600; font-size: 20px; margin: 0 0 8px; color: var(--ink); }
  .scn .scn-q { font-family: var(--serif); font-style: italic; font-size: 15px; color: var(--saffron-deep); margin: 0 0 12px; line-height: 1.45; }
  .scn p { font-size: 14.5px; line-height: 1.6; color: var(--ink-soft); margin: 0; }

  .practice { background: var(--paper-2); border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); padding: 88px 0; }
  @media (max-width: 880px) { .practice { padding: 56px 0; } }
  .practice .grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0;
    background: var(--rule); border: 1px solid var(--rule); border-radius: 20px;
    overflow: hidden; margin-top: 40px;
  }
  @media (max-width: 880px) { .practice .grid { grid-template-columns: 1fr 1fr; } }
  @media (max-width: 540px) { .practice .grid { grid-template-columns: 1fr; } }
  .step { background: var(--paper); padding: 32px 28px; display: flex; flex-direction: column; }
  .step .num {
    font-family: var(--serif-dev); font-weight: 600; font-size: 52px;
    color: var(--saffron-deep); line-height: 1; margin-bottom: 16px; letter-spacing: -0.02em;
  }
  .step h5 { font-family: var(--serif-dev); font-weight: 600; font-size: 20px; margin: 0 0 8px; color: var(--ink); }
  .step p { font-size: 14.5px; line-height: 1.55; color: var(--ink-soft); margin: 0; }

  .myth {
    background: var(--ink); color: var(--bg); border-radius: 26px; padding: 56px 48px; margin-top: 24px;
    display: grid; grid-template-columns: auto 1fr; gap: 40px; align-items: center;
  }
  @media (max-width: 720px) { .myth { grid-template-columns: 1fr; gap: 24px; padding: 36px 28px; } }
  .myth .glyph { font-family: var(--serif-dev); font-size: 120px; line-height: 1; color: var(--saffron-glow); opacity: .8; }
  .myth h3 { font-family: var(--serif-dev); font-weight: 600; font-size: clamp(24px, 2.4vw, 32px); color: var(--bg); margin: 0 0 14px; line-height: 1.25; }
  .myth p { font-family: var(--serif-dev); font-size: 18px; line-height: 1.6; color: rgba(251,246,234,.78); margin: 0 0 8px; }
  .myth .myth-label { font-family: var(--mono); font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--saffron-glow); margin-bottom: 14px; }

  .related { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 36px; }
  @media (max-width: 880px) { .related { grid-template-columns: 1fr; } }
  .rel {
    background: var(--paper); border: 1px solid var(--rule); border-radius: 18px;
    padding: 26px 24px; transition: transform .2s ease, border-color .2s ease; display: block;
  }
  .rel:hover { transform: translateY(-2px); border-color: var(--saffron-deep); }
  .rel .reltag { font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-mute); margin-bottom: 10px; }
  .rel h5 { font-family: var(--serif-dev); font-weight: 600; font-size: 20px; margin: 0 0 8px; color: var(--ink); }
  .rel p { font-size: 14.5px; line-height: 1.55; color: var(--ink-soft); margin: 0 0 14px; }
  .rel .arrow { font-family: var(--mono); font-size: 12px; letter-spacing: 0.1em; color: var(--saffron-deep); }

  .closing {
    text-align: center; padding: 100px 0 120px;
    background: radial-gradient(ellipse at top, color-mix(in oklab, var(--saffron) 14%, var(--bg)) 0%, var(--bg) 65%);
  }
  @media (max-width: 880px) { .closing { padding: 64px 0 80px; } }
  .closing .om-big { font-family: var(--serif-dev); font-size: 64px; color: var(--saffron-deep); line-height: 1; margin-bottom: 28px; }
  .closing h3 { font-family: var(--serif-dev); font-weight: 600; font-size: clamp(28px, 3vw, 42px); line-height: 1.25; margin: 0 auto 24px; max-width: 720px; text-wrap: balance; }
  .closing p { font-family: var(--serif-dev); font-size: 19px; color: var(--ink-soft); max-width: 560px; margin: 0 auto 32px; }
"""

MANDALA_SVG = """<svg class="mandala c-mandala" viewBox="0 0 200 200" aria-hidden="true">
    <g fill="none" stroke="currentColor" stroke-width="0.5">
      <circle cx="100" cy="100" r="95"/><circle cx="100" cy="100" r="78"/>
      <circle cx="100" cy="100" r="60"/><circle cx="100" cy="100" r="42"/>
      <circle cx="100" cy="100" r="24"/>
    </g>
    <g fill="none" stroke="currentColor" stroke-width="0.4">
      <g id="cp"><path d="M100 8 Q112 60 100 94 Q88 60 100 8 Z"/></g>
      <use href="#cp" transform="rotate(22.5 100 100)"/>
      <use href="#cp" transform="rotate(45 100 100)"/>
      <use href="#cp" transform="rotate(67.5 100 100)"/>
      <use href="#cp" transform="rotate(90 100 100)"/>
      <use href="#cp" transform="rotate(112.5 100 100)"/>
      <use href="#cp" transform="rotate(135 100 100)"/>
      <use href="#cp" transform="rotate(157.5 100 100)"/>
      <use href="#cp" transform="rotate(180 100 100)"/>
      <use href="#cp" transform="rotate(202.5 100 100)"/>
      <use href="#cp" transform="rotate(225 100 100)"/>
      <use href="#cp" transform="rotate(247.5 100 100)"/>
      <use href="#cp" transform="rotate(270 100 100)"/>
      <use href="#cp" transform="rotate(292.5 100 100)"/>
      <use href="#cp" transform="rotate(315 100 100)"/>
      <use href="#cp" transform="rotate(337.5 100 100)"/>
    </g>
  </svg>"""


def render_compare(data):
    if not data.get('compare_key'):
        return ''
    rows = data['compare_rows']
    headers = data.get('compare_headers', [])
    n_content = len(headers) - 1  # first col is empty label column

    # 2-column: dark/light card layout
    if n_content == 2:
        left_title = headers[1] if len(headers) > 1 else ''
        right_title = headers[2] if len(headers) > 2 else ''
        left_items, right_items = [], []
        for row in rows:
            if len(row) >= 3:
                label = re.sub(r'\*\*', '', row[0]).strip()
                left_val = parse_inline(row[1])
                right_val = parse_inline(row[2])
                left_items.append(f'<li style="font-size:16px;line-height:1.55;color:var(--ink-soft);margin-bottom:8px;"><strong style="color:var(--ink);font-size:14px;">{label}</strong><br/>{left_val}</li>')
                right_items.append(f'<li style="font-size:16px;line-height:1.55;color:rgba(251,246,234,.78);margin-bottom:8px;"><strong style="color:var(--saffron-glow);font-size:14px;">{label}</strong><br/>{right_val}</li>')
        left_list = '<ul style="margin:0 0 0 16px;padding:0;">' + ''.join(left_items) + '</ul>' if left_items else ''
        right_list = '<ul style="margin:0 0 0 16px;padding:0;">' + ''.join(right_items) + '</ul>' if right_items else ''
        return f'''
      <div class="compare">
        <div class="compare-col">
          <h5>{left_title}</h5>
          {left_list}
        </div>
        <div class="compare-col dark">
          <h5>{right_title}</h5>
          {right_list}
        </div>
      </div>'''

    # 3+ columns: styled HTML table
    col_titles = headers[1:]  # skip empty label column
    th_cells = ''.join(f'<th style="font-family:var(--mono);font-size:11px;letter-spacing:0.15em;text-transform:uppercase;color:var(--saffron-deep);padding:10px 14px;text-align:left;border-bottom:1px solid var(--rule);">{t}</th>' for t in col_titles)
    table_rows = ''
    for row in rows:
        label = parse_inline(re.sub(r'\*\*', '', row[0]).strip()) if row else ''
        td_cells = ''.join(
            f'<td style="font-family:var(--serif-dev);font-size:15px;line-height:1.5;color:var(--ink-soft);padding:10px 14px;border-bottom:1px solid var(--rule);">{parse_inline(row[i]) if i < len(row) else ""}</td>'
            for i in range(1, len(headers))
        )
        table_rows += f'<tr><td style="font-family:var(--mono);font-size:12px;font-weight:600;color:var(--ink);padding:10px 14px;border-bottom:1px solid var(--rule);white-space:nowrap;">{label}</td>{td_cells}</tr>'
    return f'''
      <div style="overflow-x:auto;margin-top:32px;">
        <table style="width:100%;border-collapse:collapse;background:var(--paper);border:1px solid var(--rule);border-radius:16px;overflow:hidden;">
          <thead><tr><th style="padding:10px 14px;border-bottom:1px solid var(--rule);"></th>{th_cells}</tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </div>'''


def render_scenarios(data):
    cards = []
    for i, sc in enumerate(data.get('scenarios', [])):
        icon = ICONS[i % len(ICONS)]
        title = sc['title']
        situation = parse_inline(sc['situation'])
        perspective = parse_inline(sc['perspective'])
        cards.append(f'''        <div class="scn">
          <div class="ic">{icon}</div>
          <h4>{title}</h4>
          <p class="scn-q">"{situation}"</p>
          <p>{perspective}</p>
        </div>''')
    return '\n'.join(cards)


def render_steps(steps):
    html = []
    for s in steps:
        html.append(f'''      <div class="step">
        <div class="num">{s['num']}</div>
        <h5>{s['title']}</h5>
        <p>{s['action']}</p>
      </div>''')
    return '\n'.join(html)


def render_related(related, catalog):
    cards = []
    for r in related[:3]:
        slug = catalog.get(r['name'], '#')
        href = f'./{slug}.html' if slug != '#' else '#'
        cards.append(f'''      <a href="{href}" class="rel">
        <div class="reltag">{r['ref']}</div>
        <h5>{r['name']}</h5>
        <p>{parse_inline(r['desc'])}</p>
        <div class="arrow">वाचा →</div>
      </a>''')
    return '\n'.join(cards)


def render_myth(data):
    if not data.get('myth_title'):
        return ''
    myth_body = data['myth_body']
    # Remove the blockquote bold title line (already in myth_title)
    myth_body = re.sub(r'^> \*\*.+?\*\*.*$', '', myth_body, flags=re.MULTILINE).strip()
    # Split into paragraphs
    paras = [p.strip() for p in myth_body.split('\n\n') if p.strip()]
    para_html = ''
    for p in paras:
        p = re.sub(r'^> ', '', p, flags=re.MULTILINE).strip()
        if p:
            para_html += f'<p>{parse_inline(p)}</p>\n'
    return f'''      <div class="myth">
        <div class="glyph">"</div>
        <div>
          <div class="myth-label">सर्वसामान्य चुकीचा अर्थ</div>
          <h3>{data['myth_title']}</h3>
          {para_html}
        </div>
      </div>'''


def generate_html(data, catalog):
    title = data['title']
    adhyay_num = data.get('adhyay_num')
    adhyay_dev = data.get('adhyay_dev')
    adhyay_url = f'../adhyay?id={adhyay_num}' if adhyay_num else '../adhyay'
    adhyay_label = f'अध्याय {adhyay_dev} वाचा' if adhyay_dev else 'अध्याय वाचा'
    # Split title for display: try to emphasise last word
    title_parts = title.split()
    if len(title_parts) >= 2:
        display_title = ' '.join(title_parts[:-1]) + f'<br/><em>{title_parts[-1]}.</em>'
    else:
        display_title = f'<em>{title}.</em>'

    subtitle = data['kendra_def'] if data['kendra_def'] else data['kendra_quote']
    shloka_lines = data['shloka_sanskrit'].replace('\n', '<br/>')
    ovi_lines = data['shloka_ovi'].replace('\n', '<br/>')

    compare_html = render_compare(data)
    scenarios_html = render_scenarios(data)
    steps_html = render_steps(data.get('steps', []))
    related_html = render_related(data.get('related', []), catalog)
    myth_html = render_myth(data)

    # Vivechan section
    vivechan_body_html = paragraphs_html(data['vivechan_body'])
    vivechan_ovi_html = ''
    if data['vivechan_ovi']:
        ovi_text = data['vivechan_ovi'].replace('\n', '<br/>')
        trans = data['vivechan_translation']
        trans_html = f'<p style="font-family:var(--serif-dev);font-size:16px;color:var(--ink-soft);margin:16px 0 0;padding-top:16px;border-top:1px dashed var(--rule);">"{trans}"</p>' if trans else ''
        vivechan_ovi_html = f'''      <div style="background:var(--paper);border:1px solid var(--rule);border-radius:20px;padding:32px 32px;margin-top:24px;">
        <div style="font-family:var(--mono);font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:var(--saffron-deep);margin-bottom:14px;">{data['vivechan_ovi_label']}</div>
        <p style="font-family:var(--serif-dev);font-style:italic;font-size:21px;line-height:1.55;color:var(--ink);margin:0;">{ovi_text}</p>
        {trans_html}
      </div>'''

    arth_html = paragraphs_html(data['arth_body'])
    kendra_html = paragraphs_html(data['kendra_body'])

    # Saar
    saar_quote = data['saar_quote']
    saar_meaning = data['saar_meaning']
    saar_html = ''
    if saar_quote:
        saar_html = f'<p style="font-family:var(--serif-dev);font-style:italic;font-size:20px;line-height:1.6;color:var(--ink);margin:0 0 12px;">{parse_inline(saar_quote)}</p>'
    if saar_meaning:
        saar_html += f'<p style="font-family:var(--serif-dev);font-weight:600;font-size:18px;color:var(--saffron-deep);margin:0 0 28px;">{saar_meaning}</p>'

    return f'''<!doctype html>
<html lang="mr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} — संकल्पना · गीता-ज्ञानेश्वरी</title>
<meta name="theme-color" content="#9c4a10" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="../css/style.css" />
<style>
{STYLE_BLOCK}
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
      <a href="../concept" class="on">संकल्पना</a>
      <a href="#">बद्दल</a>
      <a href="#" class="nav-cta">वाचन सुरू</a>
    </nav>
    <button class="menu-btn" id="menu-btn" aria-label="मेनू" aria-expanded="false">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
  <div class="mobile-nav" id="mobile-nav" aria-hidden="true">
    <div class="wrap">
      <a href="../">होम</a>
      <a href="../#chapters">अध्याय</a>
      <a href="../concept" class="on">संकल्पना</a>
    </div>
  </div>
</header>

<!-- HERO -->
<section class="c-hero">
  {MANDALA_SVG}

  <div class="wrap">
    <div class="crumb">
      <a href="../">होम</a>
      <span class="sep">/</span>
      <a href="../concept">संकल्पना</a>
      <span class="sep">/</span>
      <span class="now">{title}</span>
    </div>

    <div class="c-hero-inner">
      <div class="reveal">
        <div class="eyebrow-dev">गीतेची केंद्रीय संकल्पना</div>
        <h1 class="c-title">{display_title}</h1>
        <p class="c-sub">{subtitle}</p>

        <div style="display:flex;flex-wrap:wrap;gap:12px;">
          <a href="#practice" class="btn btn-primary">रोजच्या जीवनात कसे आणावे?</a>
          <a href="{adhyay_url}" class="btn btn-ghost">{adhyay_label}</a>
        </div>
      </div>

      <div class="reveal origin-card">
        <span class="corner">मूळ श्लोक</span>
        <div class="head">{data['shloka_source']}</div>
        <p class="shloka">{shloka_lines}</p>

        <div class="ovi-label">{data['ovi_label']}</div>
        <p class="ovi">{ovi_lines}</p>

        <div class="source">श्रीकृष्ण → अर्जुन · कुरुक्षेत्र</div>
      </div>
    </div>
  </div>
</section>

<!-- BODY -->
<section class="c-body">
  <div class="wrap-narrow">

    <!-- Meaning -->
    <div class="c-section">
      <div class="eyebrow-dev">अर्थ</div>
      <h2>संकल्पनेचा गाभा.</h2>
      {arth_html}
      {compare_html}
    </div>

    <!-- Dnyaneshwari -->
    <div class="c-section">
      <div class="eyebrow-dev">ज्ञानेश्वरी विवेचन</div>
      <h2>संत ज्ञानेश्वर हे श्लोक सामान्य माणसासाठी कसे उघडतात?</h2>
      {vivechan_body_html}
      {vivechan_ovi_html}
    </div>

    <!-- Modern scenarios -->
    <div class="c-section" id="modern">
      <div class="eyebrow-dev">आधुनिक प्रसंग</div>
      <h2>आजच्या जीवनात ही संकल्पना कुठे उभी राहते?</h2>
      <p class="body">तत्त्वज्ञानाची खरी कसोटी कार्यालयात, स्वयंपाकघरात आणि निर्णयाच्या क्षणी होते.</p>

      <div class="scenarios">
{scenarios_html}
      </div>
    </div>

    <!-- Myth callout -->
    <div class="c-section">
      <div class="eyebrow-dev">गैरसमज</div>
      <h2>ही संकल्पना समजण्यात सहसा होणारी चूक.</h2>
{myth_html}
    </div>
  </div>
</section>

<!-- PRACTICE -->
<section class="practice" id="practice">
  <div class="wrap-narrow">
    <div class="eyebrow-dev">रोजच्या जीवनात</div>
    <h2 class="section-title" style="margin-top:14px;">चार पावले — आजपासून सुरू करण्यासाठी.</h2>
    <p style="font-family:var(--serif-dev);font-size:18px;color:var(--ink-soft);max-width:640px;margin:0;line-height:1.6;">एका दिवसात हे साधता येत नाही — पण रोज एक छोटा सराव केला, तर महिन्याभरात मनाची दिशा बदलते.</p>

    <div class="grid">
{steps_html}
    </div>
  </div>
</section>

<!-- RELATED -->
<section class="c-body" style="padding-top:80px;padding-bottom:40px;">
  <div class="wrap-narrow">
    <div class="eyebrow-dev">पुढे वाचा</div>
    <h2 class="section-title" style="margin:14px 0 14px;">संबंधित संकल्पना.</h2>
    <p style="font-family:var(--serif-dev);font-size:18px;color:var(--ink-soft);max-width:560px;margin:0;line-height:1.55;">{title} समजली, तर पुढच्या तीन संकल्पना नैसर्गिकपणे उघडतात.</p>

    <div class="related">
{related_html}
    </div>
  </div>
</section>

<!-- CLOSING -->
<section class="closing">
  <div class="wrap-narrow">
    <div class="om-big">ॐ</div>
    {saar_html}
    <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:28px;">
      <a href="{adhyay_url}" class="btn btn-primary">{adhyay_label}</a>
      <a href="../concept" class="btn btn-ghost">दुसरी संकल्पना</a>
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
        <a href="{adhyay_url}">{adhyay_label}</a>
        <a href="../concept">संकल्पना</a>
      </div>
      <div>
        <h5>अभ्यास</h5>
        <a href="#">आजचा श्लोक</a>
        <a href="#">माझ्या नोंदी</a>
        <a href="#">वाचन प्रगती</a>
      </div>
      <div>
        <h5>बद्दल</h5>
        <a href="#">उद्देश</a>
        <a href="#">स्रोत</a>
        <a href="#">संपर्क</a>
      </div>
    </div>
    <div class="foot-bottom">
      <div>© २०२६ गीता-ज्ञानेश्वरी · प्रेमाने बनवलेले.</div>
      <div class="right">"योगः कर्मसु कौशलम्" — गीता २.५०</div>
    </div>
  </div>
</footer>

<script>
  const io = new IntersectionObserver((entries) => {{
    entries.forEach(e => {{ if (e.isIntersecting) e.target.classList.add('in'); }});
  }}, {{ threshold: 0.1 }});
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  document.querySelectorAll('a[href^="#"]').forEach(a => {{
    a.addEventListener('click', (e) => {{
      const id = a.getAttribute('href');
      if (id.length < 2) return;
      const t = document.querySelector(id);
      if (!t) return;
      e.preventDefault();
      window.scrollTo({{ top: t.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' }});
    }});
  }});
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


def generate_index_html(slugs):
    slugs_js = ', '.join(f'"{s}"' for s in slugs)
    return f'''<!doctype html>
<html lang="mr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>संकल्पना · गीता-ज्ञानेश्वरी</title>
<meta name="theme-color" content="#9c4a10" />
<script>
  var slugs = [{slugs_js}];
  window.location.replace(slugs[Math.floor(Math.random() * slugs.length)] + '.html');
</script>
<noscript>
  <meta http-equiv="refresh" content="0;url=nishkam-karmayog.html" />
</noscript>
</head>
<body>
  <p style="font-family:sans-serif;text-align:center;padding:60px 20px;color:#555;">
    संकल्पना उघडत आहे… <a href="nishkam-karmayog.html">येथे क्लिक करा</a>
  </p>
</body>
</html>'''


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    catalog = build_catalog()
    print(f"Catalog: {len(catalog)} concepts")

    generated = []
    for slug in SLUGS:
        p = SOURCE_DIR / f"{slug}.md"
        if not p.exists():
            print(f"  SKIP {slug} (file not found)")
            continue
        data = parse_file(p)
        html = generate_html(data, catalog)
        out_path = OUTPUT_DIR / f"{slug}.html"
        out_path.write_text(html, encoding='utf-8')
        generated.append(slug)
        print(f"  ✓ {slug}.html  ({data['title']})")

    # Write index.html
    index_html = generate_index_html(generated)
    (OUTPUT_DIR / 'index.html').write_text(index_html, encoding='utf-8')
    print(f"\nWrote sankalpana/index.html (random redirect, {len(generated)} slugs)")
    print(f"\nDone — {len(generated)} pages in {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
