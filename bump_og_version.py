#!/usr/bin/env python3
"""
bump_og_version.py
------------------
Forces WhatsApp to re-fetch OG images by adding/incrementing ?v=N
on the og:image URL in shim pages.

Usage:
    # Bump ALL shim pages
    python3 bump_og_version.py

    # Bump only a specific adhyay
    python3 bump_og_version.py 1

    # Bump a specific adhyay + concept
    python3 bump_og_version.py 1 3
"""

import os, re, sys

PROJECT  = os.path.dirname(os.path.abspath(__file__))
SHIM_DIR = os.path.join(PROJECT, "c")

# Which adhyays / concepts to bump
target_adhyay   = int(sys.argv[1]) if len(sys.argv) > 1 else None
target_concept  = int(sys.argv[2]) if len(sys.argv) > 2 else None

# Regex: matches og:image content URL with or without existing ?v=N
OG_IMG_RE = re.compile(
    r'(<meta property="og:image" content="[^"]+?)((?:\?v=\d+)?)(">)'
)

bumped = 0

for adhyay_dir in sorted(os.listdir(SHIM_DIR)):
    if not adhyay_dir.isdigit():
        continue
    aid = int(adhyay_dir)
    if target_adhyay and aid != target_adhyay:
        continue

    adhyay_path = os.path.join(SHIM_DIR, adhyay_dir)
    for concept_dir in sorted(os.listdir(adhyay_path), key=lambda x: int(x) if x.isdigit() else 0):
        if not concept_dir.isdigit():
            continue
        cid = int(concept_dir)
        if target_concept and cid != target_concept:
            continue

        fpath = os.path.join(adhyay_path, concept_dir, "index.html")
        if not os.path.exists(fpath):
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        def bump_version(m):
            current = m.group(2)   # e.g. "" or "?v=2"
            v = int(current[3:]) if current else 1
            return f'{m.group(1)}?v={v + 1}{m.group(3)}'

        new_content = OG_IMG_RE.sub(bump_version, content)

        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            # Extract new version for display
            m = OG_IMG_RE.search(new_content)
            ver = m.group(2) if m else "?"
            print(f"  ✅ c/{aid}/{cid}/index.html  →  og:image {ver}")
            bumped += 1

print(f"\nDone — {bumped} shim page(s) updated.")
