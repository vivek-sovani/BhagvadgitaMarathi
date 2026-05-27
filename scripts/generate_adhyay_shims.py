#!/usr/bin/env python3
"""
Generate /c/{adhyayId}/index.html shim pages for all 18 adhyays.

Uses home-banner-landscape.jpg (1376x768, landscape) as the OG image
for all chapters — WhatsApp requires landscape images for preview cards.
Portrait images (summary.jpg, concept images) are silently ignored by
WhatsApp's link preview crawler.

Run from the project root:
    python3 scripts/generate_adhyay_shims.py
"""

import os

BASE_URL      = "https://vivek-sovani.github.io/BhagvadgitaMarathi"
# Use landscape banner for all — WhatsApp only shows landscape OG images
OG_IMAGE      = f"{BASE_URL}/assets/home-banner-landscape.jpg"
OG_IMAGE_W    = 1376
OG_IMAGE_H    = 768

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


def has_summary(adhyay_id):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.isfile(os.path.join(root, "assets", f"adhyay-{adhyay_id}", "summary.jpg"))


def main():
    root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    created = 0

    for a in ADHYAYS:
        aid     = a["id"]
        out_dir = os.path.join(root, "c", str(aid))
        out_f   = os.path.join(out_dir, "index.html")

        os.makedirs(out_dir, exist_ok=True)

        redirect    = f"{BASE_URL}/adhyay.html?id={aid}"
        og_url      = f"{BASE_URL}/c/{aid}/"
        og_title    = f"{a['emoji']} अध्याय {a['number']} · {a['name']} | गीता-ज्ञानेश्वरी"
        page_title  = f"अध्याय {a['number']} · {a['name']}"

        # Always use landscape banner — WhatsApp only previews landscape OG images
        html = SHIM.format(
            og_url=og_url, og_title=og_title,
            og_image=OG_IMAGE, og_w=str(OG_IMAGE_W), og_h=str(OG_IMAGE_H),
            twitter_card="summary_large_image",
            redirect=redirect, page_title=page_title,
        )

        with open(out_f, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Created: c/{aid}/index.html")
        created += 1

    print(f"\nDone — {created} adhyay shim pages created.")


if __name__ == "__main__":
    main()
