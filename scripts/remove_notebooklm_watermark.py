#!/usr/bin/env python3
"""
Remove NotebookLM watermarks from JPEG images and PDF slide files.

NotebookLM embeds a small "🔔 NotebookLM" badge in the bottom-right corner of
exported slides. This script detects that corner region and fills it with the
surrounding background colour, leaving the rest of the slide untouched.

Supports:
  - JPEG / JPG files (direct pixel inpainting)
  - PDF files whose pages are image-based (modifies the embedded JPEG/PNG per page)
  - PDF files with a text layer (redacts matching text via PyMuPDF)

Usage:
    python remove_notebooklm_watermark.py <input> [<input> ...] [options]

    # Single file
    python remove_notebooklm_watermark.py slides.pdf

    # Whole directory (recursive)
    python remove_notebooklm_watermark.py ./assets/ --recursive

    # Write cleaned copies to a separate folder (safe, non-destructive)
    python remove_notebooklm_watermark.py ./assets/ --recursive --output-dir ./cleaned/

    # Preview without writing anything
    python remove_notebooklm_watermark.py slides.pdf --dry-run

    # Save side-by-side comparison PNGs for each file (useful for QA)
    python remove_notebooklm_watermark.py slides.pdf --output-dir ./cleaned/ --compare

Options:
    --output-dir DIR   Save results here instead of overwriting originals
    --recursive        Scan directories recursively
    --dry-run          Show what would be done without writing files
    --compare          Save before/after bottom-right crop PNG next to output
"""

import argparse
import io
import sys
import re
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
    import fitz  # PyMuPDF
except ImportError as e:
    sys.exit(
        f"Missing dependency: {e}\n"
        "Install with: pip install Pillow PyMuPDF numpy"
    )

# ---------------------------------------------------------------------------
# Watermark geometry constants (expressed as fractions of image dimensions)
# Tuned on NotebookLM slide exports (1376×768 PDF pages, 1143×2048 JPEGs).
# ---------------------------------------------------------------------------
WM_HEIGHT_FRAC = 0.04   # bottom 4 % of image height
WM_WIDTH_FRAC  = 0.20   # rightmost 20 % of image width
WM_MIN_H = 20           # never go below this many pixels tall
WM_MAX_H = 60           # cap to avoid eating real content
WM_MIN_W = 150          # minimum width of fill region
WM_MAX_W = 320          # maximum width of fill region

# Patterns that identify a NotebookLM text-layer watermark (text PDFs only)
_WM_PATTERNS = [
    re.compile(r"made\s+with\s+notebooklm", re.IGNORECASE),
    re.compile(r"notebooklm",               re.IGNORECASE),
    re.compile(r"notebook\s*lm",            re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Core image-level watermark removal
# ---------------------------------------------------------------------------

def _wm_bounds(h: int, w: int) -> tuple[int, int, int, int]:
    """Return (y0, y1, x0, x1) of the watermark fill region."""
    wm_h = max(WM_MIN_H, min(WM_MAX_H, int(h * WM_HEIGHT_FRAC)))
    wm_w = max(WM_MIN_W, min(WM_MAX_W, int(w * WM_WIDTH_FRAC)))
    return h - wm_h, h, w - wm_w, w


def _sample_background(arr: np.ndarray, y0: int, y1: int, x0: int, x1: int,
                        margin: int = 20) -> np.ndarray:
    """
    Estimate the background colour by sampling rows above, below, and to the
    left of the watermark bounding box.
    """
    h, w, nc = arr.shape
    bands: list[np.ndarray] = []

    above = arr[max(0, y0 - margin): y0, x0: x1]
    if above.size > 0:
        bands.append(above.reshape(-1, nc))

    below = arr[y1: min(h, y1 + margin), x0: x1]
    if below.size > 0:
        bands.append(below.reshape(-1, nc))

    left = arr[y0: y1, max(0, x0 - margin): x0]
    if left.size > 0:
        bands.append(left.reshape(-1, nc))

    if not bands:
        return np.zeros(nc, dtype=np.uint8)

    all_px = np.concatenate(bands, axis=0)
    return np.median(all_px, axis=0).astype(np.uint8)


def _remove_watermark(arr: np.ndarray) -> np.ndarray:
    """
    Inpaint the bottom-right watermark corner of an RGB(A) uint8 array.
    Returns a copy with the badge region filled with the background colour.
    """
    h, w = arr.shape[:2]
    nc = arr.shape[2] if arr.ndim == 3 else 1

    y0, y1, x0, x1 = _wm_bounds(h, w)
    bg = _sample_background(arr, y0, y1, x0, x1)

    out = arr.copy()
    out[y0:y1, x0:x1] = bg
    return out


def _has_watermark_content(arr: np.ndarray) -> bool:
    """
    Heuristic: return True if the watermark region differs noticeably from
    its surroundings (i.e. there is something in the corner to remove).
    """
    h, w = arr.shape[:2]
    y0, y1, x0, x1 = _wm_bounds(h, w)

    region = arr[y0:y1, x0:x1].astype(float)
    bg = _sample_background(arr, y0, y1, x0, x1).astype(float)

    # Mean absolute difference between corner region and background estimate
    diff = np.abs(region - bg).mean()
    return bool(diff > 8)   # 8/255 threshold


# ---------------------------------------------------------------------------
# JPEG processing
# ---------------------------------------------------------------------------

def _pil_to_rgb_array(img: Image.Image) -> np.ndarray:
    return np.array(img.convert("RGB"))


def _array_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8), mode="RGB")


def process_jpeg(src: Path, dst: Path, dry_run: bool, compare: bool) -> bool:
    img  = Image.open(src)
    arr  = _pil_to_rgb_array(img)
    h, w = arr.shape[:2]

    y0, y1, x0, x1 = _wm_bounds(h, w)

    if dry_run:
        status = "watermark detected" if _has_watermark_content(arr) else "no watermark detected"
        print(f"  [DRY-RUN] {src.name}: {status}  (fill region: rows {y0}–{y1}, cols {x0}–{x1})")
        return True

    cleaned = _remove_watermark(arr)
    dst.parent.mkdir(parents=True, exist_ok=True)
    _array_to_pil(cleaned).save(dst, format="JPEG", quality=95, optimize=True)

    if compare:
        _save_compare(arr, cleaned, dst.with_suffix(".compare.png"), y0, x0)

    print(f"  [OK] {src.name} → {dst}  (filled {y1-y0}×{x1-x0}px corner)")
    return True


# ---------------------------------------------------------------------------
# PDF processing
# ---------------------------------------------------------------------------

def _is_image_based(page: fitz.Page) -> bool:
    """True if the page appears to be a rasterised image (no real text)."""
    return len(page.get_text().strip()) == 0


def _process_image_page(page: fitz.Page, doc: fitz.Document,
                         compare: bool, compare_path: Path | None) -> bool:
    """
    For pages with no text layer: extract the embedded image, inpaint the
    watermark corner, and replace the image in the PDF.
    """
    imgs = page.get_images(full=True)
    if not imgs:
        return False

    xref = imgs[0][0]   # first (and usually only) full-page image

    try:
        img_data = doc.extract_image(xref)
        pil_img  = Image.open(io.BytesIO(img_data["image"])).convert("RGB")
    except Exception as e:
        print(f"    [WARN] could not extract image xref={xref}: {e}")
        return False

    arr     = _pil_to_rgb_array(pil_img)
    cleaned = _remove_watermark(arr)

    if np.array_equal(arr, cleaned):
        return False    # nothing changed

    # Encode cleaned image back to JPEG bytes
    buf = io.BytesIO()
    _array_to_pil(cleaned).save(buf, format="JPEG", quality=95)
    buf.seek(0)

    # Replace the embedded image stream using PyMuPDF's pixmap replacement
    new_pix = fitz.Pixmap(io.BytesIO(buf.getvalue()))
    page.replace_image(xref, pixmap=new_pix)

    if compare and compare_path:
        h, w = arr.shape[:2]
        y0, _, x0, _ = _wm_bounds(h, w)
        _save_compare(arr, cleaned, compare_path, y0, x0)

    return True


def _process_text_page(page: fitz.Page) -> bool:
    """For pages with a text layer: find and redact NotebookLM text."""
    found = False
    for pat in _WM_PATTERNS:
        for rect in page.search_for(pat.pattern, flags=fitz.TEXT_PRESERVE_WHITESPACE):
            page.add_redact_annot(rect + fitz.Rect(-4, -4, 4, 4), fill=(1, 1, 1))
            found = True

    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        if any(p.search(word) for p in _WM_PATTERNS):
            page.add_redact_annot(
                fitz.Rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4), fill=(1, 1, 1)
            )
            found = True

    if found:
        page.apply_redactions()
    return found


def process_pdf(src: Path, dst: Path, dry_run: bool, compare: bool) -> bool:
    doc  = fitz.open(str(src))
    npg  = len(doc)

    if dry_run:
        image_pages = sum(1 for p in doc if _is_image_based(p))
        print(f"  [DRY-RUN] {src.name}: {npg} pages, {image_pages} image-based")
        doc.close()
        return True

    changed      = False
    compare_path = dst.with_suffix(".compare.png") if compare else None

    for i, page in enumerate(doc):
        if _is_image_based(page):
            cp = compare_path.with_stem(f"{compare_path.stem}_p{i+1}") if compare_path else None
            if _process_image_page(page, doc, compare, cp):
                changed = True
        else:
            if _process_text_page(page):
                changed = True

    if not changed:
        doc.close()
        print(f"  [SKIP] {src.name}: nothing to remove")
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dst), garbage=4, deflate=True, clean=True)
    doc.close()
    print(f"  [OK] {src.name} → {dst}")
    return True


# ---------------------------------------------------------------------------
# QA helper: side-by-side comparison image
# ---------------------------------------------------------------------------

def _save_compare(before: np.ndarray, after: np.ndarray, path: Path,
                  crop_y: int, crop_x: int, strip: int = 80) -> None:
    """Save a side-by-side crop of the bottom-right corner for QA."""
    h, w = before.shape[:2]
    y0 = max(0, h - strip)
    x0 = max(0, crop_x - 20)

    b_crop = before[y0:h, x0:w]
    a_crop = after[ y0:h, x0:w]

    gap = np.full((b_crop.shape[0], 4, 3), 180, dtype=np.uint8)
    side_by_side = np.concatenate([b_crop, gap, a_crop], axis=1)
    Image.fromarray(side_by_side).save(str(path))


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

SUPPORTED = {".jpg", ".jpeg", ".pdf"}


def collect_files(inputs: list[Path], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for p in inputs:
        if p.is_file():
            if p.suffix.lower() in SUPPORTED:
                files.append(p)
            else:
                print(f"[WARN] unsupported type, skipping: {p}")
        elif p.is_dir():
            pattern = "**/*" if recursive else "*"
            for f in p.glob(pattern):
                if f.is_file() and f.suffix.lower() in SUPPORTED:
                    files.append(f)
        else:
            print(f"[WARN] not found: {p}")
    return sorted(set(files))


def build_dst(src: Path, output_dir: Path | None) -> Path:
    return output_dir / src.name if output_dir else src


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Remove NotebookLM watermarks from JPEG images and PDF slides.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("inputs", nargs="+", type=Path,
                    help="Files or directories to process")
    ap.add_argument("--output-dir", type=Path, default=None,
                    help="Destination directory (default: overwrite originals)")
    ap.add_argument("--recursive",  action="store_true",
                    help="Recurse into sub-directories")
    ap.add_argument("--dry-run",    action="store_true",
                    help="Show what would be done without writing any files")
    ap.add_argument("--compare",    action="store_true",
                    help="Save before/after comparison PNG next to each output")
    args = ap.parse_args()

    files = collect_files(args.inputs, args.recursive)
    if not files:
        sys.exit("No supported files found (.jpg, .jpeg, .pdf).")

    print(f"Processing {len(files)} file(s)...\n")
    ok = skip = fail = 0

    for src in files:
        dst = build_dst(src, args.output_dir)
        ext = src.suffix.lower()
        try:
            if ext in {".jpg", ".jpeg"}:
                result = process_jpeg(src, dst, args.dry_run, args.compare)
            else:
                result = process_pdf(src, dst, args.dry_run, args.compare)
            (ok if result else skip.__class__) and None  # type check bypass
            if result:
                ok += 1
            else:
                skip += 1
        except Exception as exc:
            import traceback
            print(f"  [ERROR] {src.name}: {exc}")
            traceback.print_exc()
            fail += 1

    print(f"\nDone — processed: {ok}, skipped: {skip}, errors: {fail}")


if __name__ == "__main__":
    main()
