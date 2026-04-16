#!/usr/bin/env python3
"""
compress_assets.py
------------------
Run from the project root:

    python3 compress_assets.py

Handles assets/adhyay-X/ folders (infographic images + PDFs).
Does NOT touch assets/og/ — use compress_og.py for that.

What it does
────────────
PNG → JPEG
  • Any .png file found → converted to .jpg (same base name), original .png deleted.
  • Max dimension: 2048 px (longest side).  Quality: 85.

JPEG compression
  • Any .jpg / .jpeg over JPEG_MAX_KB (800 KB) is re-compressed in-place.

PDF compression  (requires: pip3 install pikepdf)
  • Any .pdf over PDF_MAX_KB (800 KB) is compressed in-place using pikepdf
    (stream recompression + object deduplication — preserves visual quality).
  • Files whose name ends in 'o' before the extension (e.g. concept-1o.pdf,
    adhyayo.pdf) are treated as originals and left untouched.

Summary.jpg / summary.png  are processed the same as concept images.
"""

import os, subprocess, shutil

# ── tuneable thresholds ───────────────────────────────────────────────────────
JPEG_MAX_PX  = 2048    # max width or height for infographic images
JPEG_QUALITY = 85      # sips quality for infographic images (higher than OG)
JPEG_MAX_KB  = 800     # re-compress existing JPEGs above this size (KB)
PDF_MAX_KB   = 800     # compress PDFs above this size (KB)
# ─────────────────────────────────────────────────────────────────────────────

PROJECT      = os.path.dirname(os.path.abspath(__file__))
ASSETS_ROOT  = os.path.join(PROJECT, "assets")

# ── helpers ───────────────────────────────────────────────────────────────────

def sips_to_jpeg(src, dst, max_px=JPEG_MAX_PX, quality=JPEG_QUALITY):
    """Convert/resize any image → JPEG using macOS sips."""
    tmp = f"/tmp/_ca_{os.path.basename(dst)}"
    subprocess.run(
        ["sips", "-Z", str(max_px), src, "--out", tmp],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         tmp, "--out", dst],
        capture_output=True, check=True,
    )
    return os.path.getsize(dst) // 1024


def compress_pdf(path):
    """Compress PDF in-place using pikepdf. Returns (before_kb, after_kb)."""
    import pikepdf
    before = os.path.getsize(path) // 1024
    tmp = path + ".tmp.pdf"
    with pikepdf.open(path) as pdf:
        pdf.save(
            tmp,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            linearize=False,
        )
    after = os.path.getsize(tmp) // 1024
    # Only replace if we actually saved space (>=5% reduction)
    if after < before * 0.95:
        os.replace(tmp, path)
    else:
        os.remove(tmp)
        after = before  # no change
    return before, after


def is_original(fname):
    """Returns True for files like concept-1o.pdf, adhyayo.pdf (backup originals)."""
    base = os.path.splitext(fname)[0]
    return base.endswith("o") and len(base) > 1


# ── main walk ────────────────────────────────────────────────────────────────

png_converted   = 0
jpg_compressed  = 0
pdf_compressed  = 0
skipped         = 0
errors          = 0

for folder_name in sorted(os.listdir(ASSETS_ROOT)):
    # only process adhyay-X folders
    if not folder_name.startswith("adhyay-"):
        continue
    # skip the og sub-tree
    if folder_name == "og":
        continue

    folder = os.path.join(ASSETS_ROOT, folder_name)
    if not os.path.isdir(folder):
        continue

    print(f"\n📁 {folder_name}")

    for fname in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath):
            continue

        base, ext = os.path.splitext(fname)
        ext = ext.lower()
        rel  = os.path.relpath(fpath, PROJECT)

        # ── PNG → JPEG ────────────────────────────────────────────
        if ext == ".png":
            dst = os.path.join(folder, base + ".jpg")
            rel_dst = os.path.relpath(dst, PROJECT)
            try:
                kb = sips_to_jpeg(fpath, dst)
                os.remove(fpath)
                print(f"  ✅ PNG→JPG  {fname}  →  {os.path.basename(dst)}  ({kb} KB)")
                png_converted += 1
            except Exception as e:
                print(f"  ❌ PNG→JPG failed  {fname}: {e}")
                errors += 1

        # ── JPEG compression ──────────────────────────────────────
        elif ext in (".jpg", ".jpeg"):
            kb_now = os.path.getsize(fpath) // 1024
            if kb_now > JPEG_MAX_KB:
                try:
                    kb_after = sips_to_jpeg(fpath, fpath)
                    print(f"  🔄 JPG recompressed  {fname}  ({kb_now} KB → {kb_after} KB)")
                    jpg_compressed += 1
                except Exception as e:
                    print(f"  ❌ JPG compress failed  {fname}: {e}")
                    errors += 1
            else:
                skipped += 1

        # ── PDF compression ───────────────────────────────────────
        elif ext == ".pdf":
            if is_original(fname):
                print(f"  ⏭  original backup, skipping  {fname}")
                skipped += 1
                continue
            kb_now = os.path.getsize(fpath) // 1024
            if kb_now > PDF_MAX_KB:
                try:
                    before, after = compress_pdf(fpath)
                    saved = before - after
                    if saved > 0:
                        print(f"  🗜  PDF compressed  {fname}  ({before} KB → {after} KB, saved {saved} KB)")
                        pdf_compressed += 1
                    else:
                        print(f"  ℹ️  PDF already optimal  {fname}  ({before} KB)")
                        skipped += 1
                except ImportError:
                    print("  ⚠️  pikepdf not installed. Run: pip3 install pikepdf")
                    break
                except Exception as e:
                    print(f"  ❌ PDF compress failed  {fname}: {e}")
                    errors += 1
            else:
                skipped += 1

# ── summary ──────────────────────────────────────────────────────────────────
print(f"""
────────────────────────────────────────
Done
  PNG → JPEG converted : {png_converted}
  JPEGs recompressed   : {jpg_compressed}
  PDFs  compressed     : {pdf_compressed}
  Skipped (already OK) : {skipped}
  Errors               : {errors}
────────────────────────────────────────""")
