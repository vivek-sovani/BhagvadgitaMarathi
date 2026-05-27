#!/usr/bin/env python3
"""
insert_share_buttons.py — Surgically insert the Share button into every
existing sankalpana/*.html page.

Three insertions per file, all idempotent:
  1. <script src="../js/share.js" defer> before </head>
  2. Share button as third child in the hero CTA row, right after the
     <a href="../adhyay?id=N" class="btn btn-ghost">...</a> line.
  3. Auto-init script before </body>.

Usage:
  python3 scripts/insert_share_buttons.py --dry-run   # show diffs only
  python3 scripts/insert_share_buttons.py             # apply changes
  python3 scripts/insert_share_buttons.py --only abhaya.html bhaktiyog.html

Exits non-zero if any required anchor is missing in any target file.
"""
from __future__ import annotations
import argparse
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SANKALPANA_DIR = ROOT / "sankalpana"

SHARE_SCRIPT_LINE = '<script src="../js/share.js" defer></script>'

SHARE_BUTTON_HTML = (
    '          <button type="button" class="share-btn share-btn-inline" id="share-btn" aria-label="शेअर करा">\n'
    '            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.6" y1="13.5" x2="15.4" y2="17.5"/><line x1="15.4" y1="6.5" x2="8.6" y2="10.5"/></svg>\n'
    '            <span>शेअर करा</span>\n'
    '          </button>'
)

AUTOINIT_SCRIPT = (
    "<script>window.addEventListener('DOMContentLoaded', function () { "
    "if (window.autoInitSankalpanaShare) window.autoInitSankalpanaShare(); "
    "});</script>"
)

# Hero CTA <a> with btn btn-ghost going to ../adhyay?id=N
HERO_CTA_RE = re.compile(
    r'(<a href="\.\./adhyay\?id=\d+"\s+class="btn btn-ghost">[^<]*</a>)'
)


def patch_text(text: str) -> tuple[str, list[str]]:
    """Return (new_text, messages). Skips an insertion if its marker is already present."""
    msgs: list[str] = []
    new = text

    # 1. <head>: add the share.js script tag
    if 'js/share.js' in new:
        msgs.append('skip head (already has share.js)')
    else:
        if '</head>' not in new:
            raise ValueError('missing </head>')
        new = new.replace(
            '</head>',
            SHARE_SCRIPT_LINE + '\n</head>',
            1,
        )
        msgs.append('inserted head <script>')

    # 2. Hero CTA: insert share button after the "अध्याय N वाचा" ghost button
    if 'id="share-btn"' in new:
        msgs.append('skip hero button (already present)')
    else:
        m = HERO_CTA_RE.search(new)
        if not m:
            raise ValueError('missing hero CTA anchor (../adhyay?id=N btn btn-ghost)')
        # exactly one substitution in the hero block (first occurrence)
        replacement = m.group(1) + '\n' + SHARE_BUTTON_HTML
        new = new[:m.start()] + replacement + new[m.end():]
        msgs.append('inserted hero share button')

    # 3. </body>: auto-init
    if 'autoInitSankalpanaShare' in new:
        msgs.append('skip auto-init (already present)')
    else:
        if '</body>' not in new:
            raise ValueError('missing </body>')
        new = new.replace(
            '</body>',
            AUTOINIT_SCRIPT + '\n\n</body>',
            1,
        )
        msgs.append('inserted auto-init <script>')

    return new, msgs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true',
                    help='print diffs only; do not write files')
    ap.add_argument('--only', nargs='+', default=None,
                    help='only process these filenames (basenames under sankalpana/)')
    args = ap.parse_args()

    if not SANKALPANA_DIR.is_dir():
        print(f'sankalpana dir not found: {SANKALPANA_DIR}', file=sys.stderr)
        return 1

    files = sorted(SANKALPANA_DIR.glob('*.html'))
    # Skip the index.html redirect — it is not a destination page
    files = [f for f in files if f.name != 'index.html']
    if args.only:
        wanted = set(args.only)
        files = [f for f in files if f.name in wanted]

    if not files:
        print('no files to process', file=sys.stderr)
        return 1

    errors: list[str] = []
    patched = 0
    skipped = 0
    for fp in files:
        text = fp.read_text(encoding='utf-8')
        try:
            new, msgs = patch_text(text)
        except ValueError as e:
            errors.append(f'[ERROR] {fp.name}: {e}')
            continue

        if new == text:
            print(f'[skip ] {fp.name}  ({"; ".join(msgs)})')
            skipped += 1
            continue

        if args.dry_run:
            diff = difflib.unified_diff(
                text.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile=str(fp.relative_to(ROOT)),
                tofile=str(fp.relative_to(ROOT)) + ' (patched)',
                n=2,
            )
            sys.stdout.writelines(diff)
            print(f'\n[dry  ] {fp.name}  ({"; ".join(msgs)})')
        else:
            fp.write_text(new, encoding='utf-8')
            print(f'[patch] {fp.name}  ({"; ".join(msgs)})')
        patched += 1

    print()
    print(f'summary: {patched} {"would patch" if args.dry_run else "patched"}, '
          f'{skipped} already up to date, {len(errors)} errors')
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
