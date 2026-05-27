#!/usr/bin/env python3
"""
Generate /c/{adhyayId}/index.html shim pages for all 18 adhyays.

Uses each chapter's assets/adhyay-X/summary.jpg (portrait 1143x2048)
as the OG image. Falls back to home-banner-landscape.jpg for chapters
12-18 that don't have a summary image yet.

Run from the project root:
    python3 scripts/generate_adhyay_shims.py
"""

import os, struct

BASE_URL     = "https://vivek-sovani.github.io/BhagvadgitaMarathi"
FALLBACK_IMG = f"{BASE_URL}/assets/home-banner-landscape.jpg"
FALLBACK_W   = 1376
FALLBACK_H   = 768


def jpg_dimensions(path):
    """Return (width, height) of a JPEG by reading its SOF marker."""
    try:
        with open(path, 'rb') as f:
            data = f.read()
        i = 0
        while i < len(data) - 9:
            if data[i:i+2] in (b'\xff\xc0', b'\xff\xc2'):
                h = struct.unpack('>H', data[i+5:i+7])[0]
                w = struct.unpack('>H', data[i+7:i+9])[0]
                return w, h
            i += 1
    except Exception:
        pass
    return None

ADHYAYS = [
    {"id":  1, "number": "१",  "name": "अर्जुनविषादयोग",             "emoji": "😔"},
    {"id":  2, "number": "२",  "name": "सांख्ययोग",                  "emoji": "🧘"},
    {"id":  3, "number": "३",  "name": "कर्मयोग",                    "emoji": "🌾"},
    {"id":  4, "number": "४",  "name": "ज्ञानयोग",                   "emoji": "✨"},
    {"id":  5, "number": "५",  "name": "कर्मसंन्यासयोग",             "emoji": "⚖️"},
    {"id":  6, "number": "६",  "name": "आत्मसंयमयोग",                "emoji": "🧘"},
    {"id":  7, "number": "७",  "name": "ज्ञानविज्ञानयोग",            "emoji": "🔬"},
    {"id":  8, "number": "८",  "name": "अक्षरब्रह्मयोग",             "emoji": "🕉️"},
    {"id":  9, "number": "९",  "name": "राजविद्याराजगुह्ययोग",       "emoji": "👑"},
    {"id": 10, "number": "१०", "name": "विभूतियोग",                  "emoji": "🌌"},
    {"id": 11, "number": "११", "name": "विश्वरूपदर्शनयोग",           "emoji": "🌌"},
    {"id": 12, "number": "१२", "name": "भक्तियोग",                   "emoji": "❤️"},
    {"id": 13, "number": "१३", "name": "क्षेत्रक्षेत्रज्ञविभागयोग", "emoji": "🏞️"},
    {"id": 14, "number": "१४", "name": "गुणत्रयविभागयोग",            "emoji": "⚗️"},
    {"id": 15, "number": "१५", "name": "पुरुषोत्तमयोग",              "emoji": "🌳"},
    {"id": 16, "number": "१६", "name": "दैवासुरसम्पद्विभागयोग",      "emoji": "⚔️"},
    {"id": 17, "number": "१७", "name": "श्रद्धात्रयविभागयोग",        "emoji": "🙏"},
    {"id": 18, "number": "१८", "name": "मोक्षसंन्यासयोग",            "emoji": "🕊️"},
]

SHIM = """\
<!DOCTYPE html>
<html lang="mr">
<head>
  <meta charset="UTF-8">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{og_url}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="गीता-ज्ञानेश्वरी — आधुनिक जीवनदर्शन">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="{og_w}">
  <meta property="og:image:height" content="{og_h}">
  <meta name="twitter:card" content="{twitter_card}">
  <meta http-equiv="refresh" content="0;url={redirect}">
  <title>{page_title} | गीता-ज्ञानेश्वरी</title>
  <script>window.location.replace('{redirect}');</script>
</head>
<body>
  <a href="{redirect}">पुढे जा →</a>
</body>
</html>
"""


def main():
    root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    created = 0

    for a in ADHYAYS:
        aid        = a["id"]
        out_dir    = os.path.join(root, "c", str(aid))
        out_f      = os.path.join(out_dir, "index.html")
        os.makedirs(out_dir, exist_ok=True)

        redirect   = f"{BASE_URL}/adhyay.html?id={aid}"
        og_url     = f"{BASE_URL}/c/{aid}/"
        og_title   = f"{a['emoji']} अध्याय {a['number']} · {a['name']} | गीता-ज्ञानेश्वरी"
        page_title = f"अध्याय {a['number']} · {a['name']}"

        # Use chapter's own summary.jpg with its real dimensions; fallback to banner
        summary_path = os.path.join(root, "assets", f"adhyay-{aid}", "summary.jpg")
        dims = jpg_dimensions(summary_path)
        if dims:
            og_image = f"{BASE_URL}/assets/adhyay-{aid}/summary.jpg"
            og_w, og_h = str(dims[0]), str(dims[1])
            label = f"summary.jpg ({dims[0]}x{dims[1]})"
        else:
            og_image = FALLBACK_IMG
            og_w, og_h = str(FALLBACK_W), str(FALLBACK_H)
            label = "fallback banner"

        html = SHIM.format(
            og_url=og_url, og_title=og_title,
            og_image=og_image, og_w=og_w, og_h=og_h,
            twitter_card="summary",
            redirect=redirect, page_title=page_title,
        )

        with open(out_f, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  c/{aid}/index.html  ({label})")
        created += 1

    print(f"\nDone — {created} adhyay shim pages created.")


if __name__ == "__main__":
    main()
