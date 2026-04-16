#!/usr/bin/env python3
"""
compress_og.py
--------------
Drop PNG (or large JPG) images into any assets/og/adhyay-X/ folder,
then run this script from the project root:

    python3 compress_og.py

It will:
  1. Find all .png files under assets/og/
  2. Convert + compress them to JPEG (max 1600px wide, quality 75)
  3. Delete the original .png

Also re-compresses any .jpg that is over MAX_KB (300 KB).

The output JPEG keeps the same base name: concept-1.png → concept-1.jpg
"""

import os, subprocess, sys

PROJECT   = os.path.dirname(os.path.abspath(__file__))
OG_ROOT   = os.path.join(PROJECT, "assets", "og")
MAX_PX    = 1600      # max width OR height
QUALITY   = 75        # sips JPEG quality (0–100)
MAX_KB    = 300       # re-compress existing JPEGs above this size

def sips_compress(src, dst, max_px=MAX_PX, quality=QUALITY):
    """Resize to fit within max_px on longest side, then compress to JPEG."""
    tmp = f"/tmp/_og_compress_{os.path.basename(dst)}"
    # Step 1 – resize (fit within max_px × max_px box)
    subprocess.run(
        ["sips", "-Z", str(max_px), src, "--out", tmp],
        capture_output=True, check=True
    )
    # Step 2 – set JPEG quality
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         tmp, "--out", dst],
        capture_output=True, check=True
    )
    kb = os.path.getsize(dst) // 1024
    return kb

converted = 0
recompressed = 0
skipped = 0

for root, dirs, files in os.walk(OG_ROOT):
    dirs.sort()
    for fname in sorted(files):

        fpath = os.path.join(root, fname)
        base, ext = os.path.splitext(fname)
        ext = ext.lower()

        # ── PNG → JPEG ────────────────────────────────────────────
        if ext == ".png":
            dst = os.path.join(root, base + ".jpg")
            rel_src = os.path.relpath(fpath, PROJECT)
            rel_dst = os.path.relpath(dst, PROJECT)
            try:
                kb = sips_compress(fpath, dst)
                os.remove(fpath)
                print(f"  ✅ converted  {rel_src}  →  {rel_dst}  ({kb} KB)")
                converted += 1
            except Exception as e:
                print(f"  ❌ failed     {rel_src}: {e}")

        # ── Oversized JPEG → re-compress ─────────────────────────
        elif ext in (".jpg", ".jpeg"):
            kb_now = os.path.getsize(fpath) // 1024
            if kb_now > MAX_KB:
                rel = os.path.relpath(fpath, PROJECT)
                try:
                    kb_after = sips_compress(fpath, fpath)
                    print(f"  🔄 recompressed  {rel}  ({kb_now} KB → {kb_after} KB)")
                    recompressed += 1
                except Exception as e:
                    print(f"  ❌ failed     {rel}: {e}")
            else:
                skipped += 1

if converted == 0 and recompressed == 0:
    print("Nothing to do — no PNGs found and all JPEGs are within size limit.")
else:
    print(f"\nDone — {converted} PNG→JPEG converted, {recompressed} JPEGs recompressed, {skipped} already OK.")
